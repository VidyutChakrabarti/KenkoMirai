import random

class Agent:
    STATES = ('S', 'I', 'R', 'D')  # Susceptible, Infected, Recovered, Deceased

    def __init__(self, agent_id, lat, lng, state='S', age=None, occupation=None, income=None, daily_routine=None):
        self.agent_id = agent_id
        self.lat = lat
        self.lng = lng
        self.state = state
        self.infection_time = 0  # Count simulation steps since infection
        # Extended attributes from our digital twin concept:
        self.age = age
        self.occupation = occupation
        self.income = income
        self.daily_routine = daily_routine or []
        self.current_destination = None

    def move(self, move_range, lockdown_factor=1.0):
        # If the agent has a defined daily routine, move toward the current destination
        if self.daily_routine:
            if not self.current_destination:
                self.current_destination = self.daily_routine[0]['destination']
            dest_lat, dest_lng = self.current_destination
            # Move a fraction toward destination (simple linear interpolation)
            delta_lat = (dest_lat - self.lat) * 0.1 * lockdown_factor
            delta_lng = (dest_lng - self.lng) * 0.1 * lockdown_factor
            self.lat += delta_lat
            self.lng += delta_lng
            # Check if destination is reached; if so, cycle to the next event
            if abs(self.lat - dest_lat) < 0.0005 and abs(self.lng - dest_lng) < 0.0005:
                self.daily_routine.append(self.daily_routine.pop(0))
                self.current_destination = self.daily_routine[0]['destination']
        else:
            # Default random movement if no routine exists
            delta_lat = random.uniform(-move_range, move_range) * lockdown_factor
            delta_lng = random.uniform(-move_range, move_range) * lockdown_factor
            self.lat += delta_lat
            self.lng += delta_lng

    def distance_to(self, other):
        # Euclidean distance (for simplicity)
        return ((self.lat - other.lat) ** 2 + (self.lng - other.lng) ** 2) ** 0.5
