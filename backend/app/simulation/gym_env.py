from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from app.config import Settings, get_settings
from app.data.resources import SimulationResources, load_simulation_resources
from app.simulation.environment import CovidEnvironment


class CovidGymEnv(gym.Env[np.ndarray, int]):
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        *,
        num_agents: int = 500,
        initial_infected: int = 20,
        seed: int = 2025,
        horizon: int = 720,
        settings: Settings | None = None,
        resources: SimulationResources | None = None,
    ):
        super().__init__()
        if horizon < 1:
            raise ValueError("horizon must be positive")
        self.num_agents = num_agents
        self.initial_infected = initial_infected
        self.base_seed = seed
        self.horizon = horizon
        self.settings = settings or get_settings()
        self.resources = resources or load_simulation_resources()
        self.environment = self._new_environment(seed)
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(6,), dtype=np.float32)

    def _new_environment(self, seed: int) -> CovidEnvironment:
        return CovidEnvironment(
            num_agents=self.num_agents,
            initial_infected=self.initial_infected,
            seed=seed,
            infection_radius_km=self.settings.infection_radius_km,
            transmission_probability=self.settings.transmission_probability,
            incubation_steps=self.settings.incubation_steps,
            infectious_steps=self.settings.infectious_steps,
            base_mortality_probability=self.settings.base_mortality_probability,
            lockdown_mobility_factor=self.settings.lockdown_mobility_factor,
            population_centers=self.resources.population_centers,
            population_weights=self.resources.population_weights,
            mobility_multipliers=self.resources.mobility_multipliers,
            mobility_dates=self.resources.mobility_dates,
        )

    def _observation(self) -> np.ndarray:
        counts = self.environment.get_aggregate_counts()
        values = [counts[state] / self.num_agents for state in ("S", "E", "I", "R", "D")]
        values.append(float(self.environment.lockdown))
        return np.asarray(values, dtype=np.float32)

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        if not self.action_space.contains(action):
            raise ValueError("action must be 0 (open) or 1 (lockdown)")
        self.environment.run(1, "lockdown" if action == 1 else "open")
        summary = self.environment.history[-1]
        counts = summary["aggregate"]
        reward = -(
            float(counts["I"]) / self.num_agents
            + 4.0 * float(counts["D"]) / self.num_agents
            + 0.04 * float(action)
        )
        terminated = counts["E"] + counts["I"] == 0
        truncated = self.environment.model_time >= self.horizon
        return self._observation(), reward, terminated, truncated, {"summary": summary}

    def reset(self, *, seed: int | None = None, options: dict[str, object] | None = None) -> tuple[np.ndarray, dict[str, object]]:
        super().reset(seed=seed)
        selected_seed = self.base_seed if seed is None else seed
        self.environment = self._new_environment(selected_seed)
        return self._observation(), {"seed": selected_seed, "resource_fingerprint": self.resources.fingerprint}

    def render(self) -> None:
        summary = self.environment.get_summary()
        print(f"step={summary['time']} aggregate={summary['aggregate']} lockdown={summary['lockdown']}")
