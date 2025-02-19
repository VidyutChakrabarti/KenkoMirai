# This module wraps chain-of-thought functionality to generate daily routines.
from app.simulation.chain_of_thought import generate_chain_of_thought

def get_daily_routine(age, occupation, income):
    return generate_chain_of_thought(age, occupation, income)
