from fastapi import APIRouter
from app.api import models
from app.simulation.simulation_engine import run_simulation
from app.simulation.rl_module import simulate_rl_decision, apply_rl_decision
from app.simulation.environment import CovidEnvironment

router = APIRouter()

@router.get("/simulation", response_model=models.SimulationResult)
def get_simulation(steps: int = 50):
    """
    Run the simulation for a given number of steps.
    """
    result = run_simulation(steps=steps)
    return result

@router.post("/simulate-step", response_model=models.SimulationStep)
def simulate_step(apply_rl: bool = False):
    """
    Run a single simulation step. Optionally apply an RL decision for lockdown.
    """
    env = CovidEnvironment(num_agents=500, initial_infected=20)
    env.step()
    state = env.get_details()
    if apply_rl:
        decision = simulate_rl_decision(state)
        env = apply_rl_decision(env, decision)
        state = env.get_details()
    return state

@router.get("/health")
def health_check():
    return {"status": "ok"}
