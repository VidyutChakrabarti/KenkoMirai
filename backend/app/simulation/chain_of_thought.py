import random

def generate_chain_of_thought(age, occupation, income):
    """
    Simulate chain-of-thought reasoning to generate a realistic daily routine.
    Returns a list of events, each with a time, destination coordinates, and a purpose.
    """
    # Pre-defined destination coordinates in Los Angeles
    destinations = {
        'home': (34.05, -118.25),
        'work': (34.04, -118.27),
        'grocery': (34.06, -118.23),
        'park': (34.07, -118.24),
        'hospital': (34.03, -118.26),
        'gym': (34.05, -118.28)
    }
    
    routine = []
    # Morning at home
    routine.append({
        'time': '08:00',
        'destination': destinations['home'],
        'purpose': 'morning routine'
    })
    
    # Work or school if applicable
    if occupation in ['student', 'office_worker', 'healthcare']:
        routine.append({
            'time': '09:00',
            'destination': destinations.get('work', destinations['home']),
            'purpose': 'work'
        })
    
    # Midday activity: grocery or park break
    if random.random() > 0.5:
        routine.append({
            'time': '12:00',
            'destination': destinations.get('grocery', destinations['home']),
            'purpose': 'lunch/grocery'
        })
    else:
        routine.append({
            'time': '12:00',
            'destination': destinations.get('park', destinations['home']),
            'purpose': 'break'
        })
    
    # Afternoon return to work if applicable
    if occupation in ['student', 'office_worker', 'healthcare']:
        routine.append({
            'time': '13:00',
            'destination': destinations.get('work', destinations['home']),
            'purpose': 'resume work'
        })
    
    # Evening return home
    routine.append({
        'time': '18:00',
        'destination': destinations['home'],
        'purpose': 'evening'
    })
    
    # Optional additional activity for high-income agents
    if income == 'high' and random.random() > 0.5:
        routine.append({
            'time': '20:00',
            'destination': destinations.get('gym', destinations['home']),
            'purpose': 'exercise'
        })
    
    return routine
