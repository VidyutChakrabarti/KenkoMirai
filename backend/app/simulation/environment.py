from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import asdict, dataclass

import mesa

from app.simulation.agent import Agent
from app.simulation.agent_profile import generate_agent_profile


LOS_ANGELES_BOUNDS = (33.65, 34.85, -118.95, -117.60)
POLICIES = frozenset({"open", "lockdown", "adaptive"})
STEPS_PER_DAY = 24
POPULATION_CENTERS = (
    (34.0522, -118.2437),
    (34.0928, -118.3287),
    (34.0195, -118.4912),
    (34.0635, -118.4455),
    (34.1478, -118.1445),
    (33.9617, -118.3531),
    (34.1808, -118.3090),
    (33.9416, -118.4085),
)


@dataclass(frozen=True, slots=True)
class SimulationParameters:
    num_agents: int = 500
    initial_infected: int = 20
    seed: int = 2025
    area_bounds: tuple[float, float, float, float] = LOS_ANGELES_BOUNDS
    infection_radius_km: float = 0.18
    transmission_probability: float = 0.08
    incubation_steps: int = 72
    infectious_steps: int = 240
    base_mortality_probability: float = 0.006
    lockdown_mobility_factor: float = 0.22
    max_move_degrees: float = 0.004

    def __post_init__(self) -> None:
        if self.num_agents < 1:
            raise ValueError("num_agents must be positive")
        if not 0 <= self.initial_infected <= self.num_agents:
            raise ValueError("initial_infected must be between zero and num_agents")
        if self.infection_radius_km <= 0:
            raise ValueError("infection_radius_km must be positive")
        for name, value in (
            ("transmission_probability", self.transmission_probability),
            ("base_mortality_probability", self.base_mortality_probability),
            ("lockdown_mobility_factor", self.lockdown_mobility_factor),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between zero and one")


def _haversine_km(first: Agent, second: Agent) -> float:
    radius = 6371.0088
    lat1, lat2 = math.radians(first.lat), math.radians(second.lat)
    delta_lat = lat2 - lat1
    delta_lng = math.radians(second.lng - first.lng)
    value = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(value)))


class CovidEnvironment(mesa.Model):
    """Seeded, discrete-time SEIRD agent simulation for scenario exploration."""

    def __init__(
        self,
        num_agents: int = 500,
        initial_infected: int = 20,
        area_bounds: tuple[float, float, float, float] = LOS_ANGELES_BOUNDS,
        *,
        seed: int = 2025,
        infection_radius_km: float = 0.18,
        transmission_probability: float = 0.08,
        incubation_steps: int = 72,
        infectious_steps: int = 240,
        base_mortality_probability: float = 0.006,
        lockdown_mobility_factor: float = 0.22,
        policy: str = "open",
        population_centers: tuple[tuple[float, float], ...] | None = None,
        population_weights: tuple[float, ...] | None = None,
        mobility_multipliers: tuple[float, ...] | None = None,
        mobility_dates: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.parameters = SimulationParameters(
            num_agents=num_agents,
            initial_infected=initial_infected,
            seed=seed,
            area_bounds=area_bounds,
            infection_radius_km=infection_radius_km,
            transmission_probability=transmission_probability,
            incubation_steps=incubation_steps,
            infectious_steps=infectious_steps,
            base_mortality_probability=base_mortality_probability,
            lockdown_mobility_factor=lockdown_mobility_factor,
        )
        self.num_agents = num_agents
        self.initial_infected = initial_infected
        self.area_bounds = area_bounds
        self.model_time = 0
        if policy not in POLICIES:
            raise ValueError(f"policy must be one of {sorted(POLICIES)}")
        self.initial_policy = policy
        self.policy = policy
        self._requested_policy: str | None = None
        self.lockdown = False
        self.population_centers = population_centers or POPULATION_CENTERS
        self.population_weights = population_weights
        self.mobility_multipliers = mobility_multipliers or (1.0,)
        self.mobility_dates = mobility_dates or ()
        if not self.population_centers:
            raise ValueError("population_centers cannot be empty")
        if self.population_weights is not None:
            if len(self.population_weights) != len(self.population_centers):
                raise ValueError("population weights and centers must have the same length")
            if any(value <= 0 for value in self.population_weights):
                raise ValueError("population weights must be positive")
        if any(not 0 <= value <= 2 for value in self.mobility_multipliers):
            raise ValueError("mobility multipliers must be between zero and two")
        if self.mobility_dates and len(self.mobility_dates) != len(self.mobility_multipliers):
            raise ValueError("mobility dates and multipliers must have the same length")
        self._agents_by_id: dict[int, Agent] = {}
        self.history: list[dict[str, object]] = []
        self._rng: random.Random = self.random
        self._init_agents()
        self.set_policy(policy)
        self.history.append(self.get_summary())

    def _init_agents(self) -> None:
        min_lat, max_lat, min_lng, max_lng = self.area_bounds
        infected_ids = set(self._rng.sample(range(self.num_agents), self.initial_infected))
        for agent_id in range(self.num_agents):
            center_lat, center_lng = self._rng.choices(
                self.population_centers,
                weights=self.population_weights,
                k=1,
            )[0]
            home = (
                min(max_lat, max(min_lat, self._rng.gauss(center_lat, 0.009))),
                min(max_lng, max(min_lng, self._rng.gauss(center_lng, 0.011))),
            )
            profile = generate_agent_profile(home=home, bounds=self.area_bounds, rng=self._rng)
            agent = Agent(
                self,
                agent_id=agent_id,
                lat=home[0],
                lng=home[1],
                home_lat=home[0],
                home_lng=home[1],
                state="I" if agent_id in infected_ids else "S",
                age=profile["age"],
                occupation=profile["occupation"],
                income=profile["income"],
                daily_routine=profile["daily_routine"],
            )
            self._agents_by_id[agent_id] = agent

    def reset(self) -> dict[str, object]:
        """Restore seeded scenario state while keeping Mesa's scheduler monotonic."""
        self.model_time = 0
        self.policy = self.initial_policy
        self._requested_policy = None
        self.lockdown = False
        for agent in list(self.agents):
            agent.remove()
        self._agents_by_id.clear()
        self.history.clear()
        self.random.seed(self.parameters.seed)
        self._rng = self.random
        self._init_agents()
        self.set_policy(self.initial_policy)
        self.history.append(self.get_summary())
        return self.get_details()

    def set_policy(self, policy: str) -> str:
        if policy not in POLICIES:
            raise ValueError(f"policy must be one of {sorted(POLICIES)}")
        if policy == "adaptive":
            infected_fraction = self.get_aggregate_counts()["I"] / self.num_agents
            self.lockdown = infected_fraction >= (0.04 if self.lockdown else 0.10)
        else:
            self.lockdown = policy == "lockdown"
        self.policy = policy
        return "lockdown" if self.lockdown else "open"

    def _cell_dimensions(self) -> tuple[float, float]:
        latitude_degrees = self.parameters.infection_radius_km / 111.32
        middle_latitude = (self.area_bounds[0] + self.area_bounds[1]) / 2
        longitude_degrees = latitude_degrees / max(0.2, math.cos(math.radians(middle_latitude)))
        return latitude_degrees, longitude_degrees

    def _infectious_grid(self, infectious: list[Agent]) -> dict[tuple[int, int], list[Agent]]:
        lat_size, lng_size = self._cell_dimensions()
        grid: dict[tuple[int, int], list[Agent]] = defaultdict(list)
        for agent in infectious:
            grid[(math.floor(agent.lat / lat_size), math.floor(agent.lng / lng_size))].append(agent)
        return grid

    def _exposed_agent_ids(self, infectious: list[Agent]) -> set[int]:
        if not infectious:
            return set()
        lat_size, lng_size = self._cell_dimensions()
        grid = self._infectious_grid(infectious)
        exposed: set[int] = set()
        contact_factor = 0.55 if self.lockdown else 1.0
        for agent in self.agents:
            if agent.state != "S":
                continue
            cell = (math.floor(agent.lat / lat_size), math.floor(agent.lng / lng_size))
            contacts = 0
            for lat_offset in (-1, 0, 1):
                for lng_offset in (-1, 0, 1):
                    for source in grid.get((cell[0] + lat_offset, cell[1] + lng_offset), ()):
                        if _haversine_km(agent, source) <= self.parameters.infection_radius_km:
                            contacts += 1
            if contacts:
                probability = 1 - (1 - self.parameters.transmission_probability * contact_factor) ** contacts
                if self._rng.random() < probability:
                    exposed.add(agent.agent_id)
        return exposed

    def _mortality_probability(self, age: int) -> float:
        multiplier = 0.25 if age < 40 else 1.0 if age < 65 else 3.0 if age < 80 else 6.0
        return min(0.95, self.parameters.base_mortality_probability * multiplier)

    def _baseline_mobility(self) -> tuple[float, str | None]:
        day_index = max(0, self.model_time - 1) // STEPS_PER_DAY
        index = day_index % len(self.mobility_multipliers)
        date = self.mobility_dates[index] if self.mobility_dates else None
        return self.mobility_multipliers[index], date

    def step(self) -> None:
        policy = self._requested_policy
        if policy is not None:
            self.set_policy(policy)
        elif self.policy == "adaptive":
            self.set_policy("adaptive")
        self.model_time += 1
        baseline_mobility, _ = self._baseline_mobility()
        policy_factor = self.parameters.lockdown_mobility_factor if self.lockdown else 1.0
        mobility = baseline_mobility * policy_factor
        self.agents.do(
            "move",
            hour=self.model_time % STEPS_PER_DAY,
            mobility_factor=mobility,
            max_move_degrees=self.parameters.max_move_degrees,
            bounds=self.area_bounds,
            rng=self._rng,
        )

        infectious = [agent for agent in self.agents if agent.state == "I"]
        exposed_ids = self._exposed_agent_ids(infectious)
        new_infectious = 0
        new_recoveries = 0
        new_deaths = 0
        for agent in self.agents:
            if agent.state == "E":
                agent.state_time += 1
                if agent.state_time >= self.parameters.incubation_steps:
                    agent.state = "I"
                    agent.state_time = 0
                    new_infectious += 1
            elif agent.state == "I":
                agent.state_time += 1
                if agent.state_time >= self.parameters.infectious_steps:
                    if self._rng.random() < self._mortality_probability(agent.age):
                        agent.state = "D"
                        new_deaths += 1
                    else:
                        agent.state = "R"
                        new_recoveries += 1
                    agent.state_time = 0

        for agent_id in exposed_ids:
            agent = self._agents_by_id[agent_id]
            if agent.state == "S":
                agent.state = "E"
                agent.state_time = 0

        summary = self.get_summary(
            new_exposures=len(exposed_ids),
            new_infectious=new_infectious,
            new_recoveries=new_recoveries,
            new_deaths=new_deaths,
            exposure_ratio=round(len(exposed_ids) / max(1, len(infectious)), 4),
        )
        self.history.append(summary)

    def run(self, steps: int, policy: str | None = None) -> dict[str, object]:
        if steps < 1:
            raise ValueError("steps must be positive")
        if policy is not None and policy not in POLICIES:
            raise ValueError(f"policy must be one of {sorted(POLICIES)}")
        self._requested_policy = policy
        try:
            self.run_for(steps)
        finally:
            self._requested_policy = None
        return self.get_details()

    def get_aggregate_counts(self) -> dict[str, int]:
        counts = {state: 0 for state in ("S", "E", "I", "R", "D")}
        for agent in self.agents:
            counts[agent.state] += 1
        return counts

    def get_summary(self, **events: int | float) -> dict[str, object]:
        mobility_multiplier, mobility_date = self._baseline_mobility()
        effective_mobility = mobility_multiplier * (self.parameters.lockdown_mobility_factor if self.lockdown else 1.0)
        return {
            "time": self.model_time,
            "elapsed_days": round(self.model_time / STEPS_PER_DAY, 4),
            "hour_of_day": self.model_time % STEPS_PER_DAY,
            "aggregate": self.get_aggregate_counts(),
            "lockdown": self.lockdown,
            "active_policy": self.policy,
            "new_exposures": int(events.get("new_exposures", 0)),
            "new_infectious": int(events.get("new_infectious", 0)),
            "new_recoveries": int(events.get("new_recoveries", 0)),
            "new_deaths": int(events.get("new_deaths", 0)),
            "exposure_ratio": float(events.get("exposure_ratio", 0.0)),
            "mobility_multiplier": round(effective_mobility, 4),
            "mobility_date": mobility_date,
        }

    def get_details(self, *, include_agents: bool = True) -> dict[str, object]:
        summary = dict(self.history[-1]) if self.history else self.get_summary()
        summary.update(
            time=self.model_time,
            aggregate=self.get_aggregate_counts(),
            lockdown=self.lockdown,
            active_policy=self.policy,
        )
        return {
            **summary,
            "agents": [agent.serialize() for agent in self.agents] if include_agents else [],
        }

    def configuration(self) -> dict[str, object]:
        return {
            **asdict(self.parameters),
            "time_unit": "hour",
            "steps_per_day": STEPS_PER_DAY,
            "initial_policy": self.initial_policy,
            "agent_framework": "Mesa 3",
        }
