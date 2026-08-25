from __future__ import annotations

import uuid

from app.config import Settings, get_settings
from app.data.resources import SimulationResources, load_simulation_resources
from app.simulation.environment import CovidEnvironment


def run_simulation(
    *,
    steps: int = 168,
    num_agents: int | None = None,
    initial_infected: int | None = None,
    seed: int | None = None,
    policy: str = "open",
    include_agents: bool = True,
    settings: Settings | None = None,
    resources: SimulationResources | None = None,
) -> dict[str, object]:
    settings = settings or get_settings()
    resources = resources or load_simulation_resources()
    agents = num_agents if num_agents is not None else settings.default_agents
    infected = initial_infected if initial_infected is not None else min(20, agents)
    if agents > settings.max_agents:
        raise ValueError(f"num_agents cannot exceed {settings.max_agents}")
    if steps > settings.max_steps_per_request:
        raise ValueError(f"steps cannot exceed {settings.max_steps_per_request}")
    selected_seed = settings.default_seed if seed is None else seed
    environment = CovidEnvironment(
        num_agents=agents,
        initial_infected=infected,
        seed=selected_seed,
        infection_radius_km=settings.infection_radius_km,
        transmission_probability=settings.transmission_probability,
        incubation_steps=settings.incubation_steps,
        infectious_steps=settings.infectious_steps,
        base_mortality_probability=settings.base_mortality_probability,
        lockdown_mobility_factor=settings.lockdown_mobility_factor,
        policy=policy,
        population_centers=resources.population_centers,
        population_weights=resources.population_weights,
        mobility_multipliers=resources.mobility_multipliers,
        mobility_dates=resources.mobility_dates,
    )
    environment.run(steps, policy)
    simulation_id = str(uuid.uuid4())
    return {
        "simulation_id": simulation_id,
        "seed": selected_seed,
        "model_version": "mesa-seird-agent-v2",
        "resources": resources.metadata(),
        "configuration": environment.configuration(),
        "final": {
            "simulation_id": simulation_id,
            **environment.get_details(include_agents=include_agents),
        },
        "history": environment.history,
    }
