import random
from app.simulation.chain_of_thought import generate_chain_of_thought

def generate_agent_profile(agent_id, lat, lng):
    # Generate basic demographic info
    age = random.randint(18, 80)
    occupation = random.choice(['student', 'office_worker', 'retired', 'healthcare', 'service'])
    income = random.choice(['low', 'medium', 'high'])
    
    # Generate daily routine using chain-of-thought reasoning
    routine = generate_daily_routine(age, occupation, income)
    
    profile = {
        'age': age,
        'occupation': occupation,
        'income': income,
        'daily_routine': routine
    }
    return profile

def generate_daily_routine(age, occupation, income):
    # Generate a daily routine based on agent demographics
    return generate_chain_of_thought(age, occupation, income)
