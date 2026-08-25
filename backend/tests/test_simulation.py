import mesa
import pytest

from app.simulation.agent import Agent
from app.simulation.environment import CovidEnvironment
from app.simulation.simulation_engine import run_simulation


def test_seed_reproduces_initial_state() -> None:
    first = CovidEnvironment(num_agents=80, initial_infected=5, seed=42)
    second = CovidEnvironment(num_agents=80, initial_infected=5, seed=42)
    assert first.get_details() == second.get_details()


def test_mesa_owns_model_and_agent_lifecycle() -> None:
    environment = CovidEnvironment(num_agents=25, initial_infected=2, seed=5)
    assert isinstance(environment, mesa.Model)
    assert len(environment.agents) == 25
    assert all(isinstance(agent, Agent) for agent in environment.agents)
    assert environment.configuration()["agent_framework"] == "Mesa 3"
    environment.run(1, "open")
    assert environment.steps == 1
    assert environment.time == 1.0
    assert environment.model_time == 1


def test_population_is_conserved() -> None:
    environment = CovidEnvironment(num_agents=100, initial_infected=8, seed=9)
    for _ in range(20):
        environment.run(1, "adaptive")
        assert sum(environment.get_aggregate_counts().values()) == 100


def test_reset_restores_seeded_state() -> None:
    environment = CovidEnvironment(num_agents=60, initial_infected=4, seed=12)
    fresh_environment = CovidEnvironment(num_agents=60, initial_infected=4, seed=12)
    initial = environment.get_details()
    environment.run(5, "lockdown")
    assert environment.steps == 5
    environment.reset()
    assert environment.get_details() == initial
    assert len(environment.agents) == 60
    assert environment.steps == 5
    environment.run(1, "open")
    fresh_environment.run(1, "open")
    assert environment.model_time == 1
    assert environment.steps == 6
    assert environment.get_details() == fresh_environment.get_details()


def test_initial_policy_and_mobility_are_recorded() -> None:
    environment = CovidEnvironment(
        num_agents=50,
        initial_infected=10,
        seed=2,
        policy="adaptive",
        mobility_multipliers=(0.5,),
        mobility_dates=("2020-03-01",),
    )
    assert environment.history[0]["lockdown"] is True
    assert environment.history[0]["mobility_multiplier"] == 0.11
    assert environment.history[0]["mobility_date"] == "2020-03-01"


def test_multi_step_run_records_every_step() -> None:
    environment = CovidEnvironment(num_agents=50, initial_infected=3, seed=13)
    environment.run(10, "open")
    assert [item["time"] for item in environment.history] == list(range(11))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"num_agents": 9}, "num_agents"),
        ({"steps": 0}, "steps"),
        ({"initial_infected": 501}, "initial_infected"),
    ],
)
def test_batch_rejects_invalid_bounds(kwargs: dict[str, int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        run_simulation(**kwargs)
