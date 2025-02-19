from app.simulation.environment import CovidEnvironment

def run_simulation(steps=50):
    env = CovidEnvironment(num_agents=500, initial_infected=20)
    simulation_history = []
    for _ in range(steps):
        env.step()
        simulation_history.append(env.get_details())
    return {
        "final": env.get_details(),
        "history": simulation_history
    }
