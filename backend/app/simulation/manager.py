from __future__ import annotations

import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from app.config import Settings
from app.data.resources import SimulationResources, load_simulation_resources
from app.simulation.environment import CovidEnvironment


class SessionNotFoundError(KeyError):
    pass


class SessionCapacityError(RuntimeError):
    pass


class SimulationBusyError(RuntimeError):
    pass


@dataclass(slots=True)
class SimulationSession:
    environment: CovidEnvironment
    created_monotonic: float
    accessed_monotonic: float
    lock: threading.RLock = field(default_factory=threading.RLock)


class SimulationManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._sessions: dict[str, SimulationSession] = {}
        self._lock = threading.RLock()
        self._compute_slots = threading.BoundedSemaphore(settings.max_concurrent_runs)
        self.resources: SimulationResources = load_simulation_resources()

    @contextmanager
    def _admit_compute(self, *, num_agents: int, steps: int) -> Iterator[None]:
        work_units = num_agents * steps
        if work_units > self.settings.max_work_units:
            raise ValueError(
                f"request requires {work_units} work units; maximum is {self.settings.max_work_units}"
            )
        if not self._compute_slots.acquire(blocking=False):
            raise SimulationBusyError("simulation capacity is busy; retry the request shortly")
        try:
            yield
        finally:
            self._compute_slots.release()

    def _remove_expired_locked(self) -> None:
        cutoff = time.monotonic() - self.settings.session_ttl_seconds
        expired = [item for item in self._sessions.items() if item[1].accessed_monotonic < cutoff]
        for key, session in expired:
            if session.lock.acquire(blocking=False):
                try:
                    self._sessions.pop(key, None)
                finally:
                    session.lock.release()

    def _retained_agents_locked(self) -> int:
        return sum(session.environment.num_agents for session in self._sessions.values())

    def _check_session_capacity_locked(self, num_agents: int) -> None:
        if len(self._sessions) >= self.settings.max_sessions:
            raise SessionCapacityError("simulation session capacity reached")
        projected_agents = self._retained_agents_locked() + num_agents
        if projected_agents > self.settings.max_retained_agents:
            raise SessionCapacityError(
                f"retained population capacity would exceed {self.settings.max_retained_agents} agents"
            )

    def create(
        self,
        *,
        num_agents: int,
        initial_infected: int,
        seed: int,
        policy: str,
    ) -> tuple[str, CovidEnvironment]:
        if num_agents > self.settings.max_agents:
            raise ValueError(f"num_agents cannot exceed {self.settings.max_agents}")
        now = time.monotonic()
        with self._lock:
            self._remove_expired_locked()
            self._check_session_capacity_locked(num_agents)
        with self._admit_compute(num_agents=num_agents, steps=1):
            simulation_id = str(uuid.uuid4())
            environment = CovidEnvironment(
                num_agents=num_agents,
                initial_infected=initial_infected,
                seed=seed,
                infection_radius_km=self.settings.infection_radius_km,
                transmission_probability=self.settings.transmission_probability,
                incubation_steps=self.settings.incubation_steps,
                infectious_steps=self.settings.infectious_steps,
                base_mortality_probability=self.settings.base_mortality_probability,
                lockdown_mobility_factor=self.settings.lockdown_mobility_factor,
                policy=policy,
                population_centers=self.resources.population_centers,
                population_weights=self.resources.population_weights,
                mobility_multipliers=self.resources.mobility_multipliers,
                mobility_dates=self.resources.mobility_dates,
            )
        with self._lock:
            self._remove_expired_locked()
            self._check_session_capacity_locked(num_agents)
            self._sessions[simulation_id] = SimulationSession(environment, now, now)
            return simulation_id, environment

    def _get_session(self, simulation_id: str) -> SimulationSession:
        with self._lock:
            self._remove_expired_locked()
            session = self._sessions.get(simulation_id)
            if session is None:
                raise SessionNotFoundError(simulation_id)
            session.accessed_monotonic = time.monotonic()
            return session

    def get(self, simulation_id: str) -> CovidEnvironment:
        return self._get_session(simulation_id).environment

    def snapshot(self, simulation_id: str, *, include_agents: bool = True) -> dict[str, object]:
        session = self._get_session(simulation_id)
        with session.lock:
            return {"simulation_id": simulation_id, **session.environment.get_details(include_agents=include_agents)}

    def advance(
        self,
        simulation_id: str,
        *,
        steps: int,
        policy: str | None,
        include_agents: bool = True,
    ) -> dict[str, object]:
        if steps > self.settings.max_steps_per_request:
            raise ValueError(f"steps cannot exceed {self.settings.max_steps_per_request}")
        session = self._get_session(simulation_id)
        with session.lock:
            if session.environment.model_time + steps > self.settings.max_total_steps_per_session:
                raise ValueError(
                    f"session cannot exceed {self.settings.max_total_steps_per_session} total steps"
                )
            history_start = len(session.environment.history)
            with self._admit_compute(num_agents=session.environment.num_agents, steps=steps):
                session.environment.run(steps, policy)
            session.accessed_monotonic = time.monotonic()
            return {
                "snapshot": {
                    "simulation_id": simulation_id,
                    **session.environment.get_details(include_agents=include_agents),
                },
                "history": session.environment.history[history_start:],
            }

    def history(self, simulation_id: str, *, after: int = -1, limit: int = 1_000) -> dict[str, object]:
        session = self._get_session(simulation_id)
        with session.lock:
            matching = [item for item in session.environment.history if int(item["time"]) > after]
            items = matching[:limit]
            next_after = int(items[-1]["time"]) if items else after
            return {
                "simulation_id": simulation_id,
                "items": items,
                "next_after": next_after,
                "has_more": len(matching) > limit,
            }

    def run_batch(self, **parameters: object) -> dict[str, object]:
        from app.simulation.simulation_engine import run_simulation

        num_agents = int(parameters.get("num_agents") or self.settings.default_agents)
        steps = int(parameters.get("steps") or self.settings.default_steps)
        normalized = {**parameters, "num_agents": num_agents, "steps": steps}
        with self._admit_compute(num_agents=num_agents, steps=steps):
            return run_simulation(settings=self.settings, resources=self.resources, **normalized)

    def delete(self, simulation_id: str) -> None:
        with self._lock:
            session = self._sessions.get(simulation_id)
        if session is None:
            raise SessionNotFoundError(simulation_id)
        with session.lock:
            with self._lock:
                if self._sessions.get(simulation_id) is not session:
                    raise SessionNotFoundError(simulation_id)
                self._sessions.pop(simulation_id)

    def count(self) -> int:
        with self._lock:
            self._remove_expired_locked()
            return len(self._sessions)
