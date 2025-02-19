from app.simulation.environment import CovidEnvironment

def test_environment_reset():
    env = CovidEnvironment()
    # Artificially set state to verify reset works
    env.agents[0].state = 'I'
    env.reset()
    assert env.get_aggregate_counts()['I'] <= env.initial_infected

def test_environment_step():
    env = CovidEnvironment()
    initial_infected = env.get_aggregate_counts()['I']
    env.step()
    new_infected = env.get_aggregate_counts()['I']
    assert new_infected >= initial_infected
