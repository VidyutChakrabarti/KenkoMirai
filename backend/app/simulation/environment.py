import random
from app.simulation.agent import Agent
from app.simulation.agent_profile import generate_agent_profile

class CovidEnvironment:
    def __init__(self, num_agents=100, initial_infected=5, area_bounds=(33.90, 34.20, -118.70, -118.15)):
        """
        Digital twin of Los Angeles.
        area_bounds: (min_lat, max_lat, min_lng, max_lng)
        """
        self.num_agents = num_agents
        self.initial_infected = initial_infected
        self.area_bounds = area_bounds
        self.agents = []
        self.time = 0
        self.history = []

        # Simulation parameters
        self.move_range = 0.005           # Adjusted movement range for LA scale
        self.infection_radius = 0.005     # Proximity threshold for infection
        self.infection_prob = 0.15        # Infection probability
        self.recovery_time = 14           # Steps until recovery/death possible
        self.recovery_prob = 0.2          # Chance to recover after infection period
        self.mortality_prob = 0.03        # Chance to die after infection period

        self.lockdown = False           # Lockdown status (can be set via RL decision)
        self.lockdown_factor = 0.3      # Movement reduction factor during lockdown

        self._init_agents()

    def _init_agents(self):
        min_lat, max_lat, min_lng, max_lng = self.area_bounds
        for i in range(self.num_agents):
            lat = random.uniform(min_lat, max_lat)
            lng = random.uniform(min_lng, max_lng)
            # Generate extended agent profile
            profile = generate_agent_profile(i, lat, lng)
            state = 'S'
            if i < self.initial_infected:
                state = 'I'
            agent = Agent(
                agent_id=i,
                lat=lat,
                lng=lng,
                state=state,
                age=profile['age'],
                occupation=profile['occupation'],
                income=profile['income'],
                daily_routine=profile['daily_routine']
            )
            self.agents.append(agent)

    def reset(self):
        self.time = 0
        self.history = []
        self.agents = []
        self._init_agents()

    def step(self):
        self.time += 1

        # For demonstration, toggle lockdown every 30 steps
        if self.time % 30 == 0:
            self.lockdown = not self.lockdown

        movement_factor = self.lockdown_factor if self.lockdown else 1.0

        # Agents move (using their daily routines if defined)
        for agent in self.agents:
            if agent.state != 'D':
                agent.move(self.move_range, movement_factor)

        # Process infections and state transitions
        for agent in self.agents:
            if agent.state == 'I':
                agent.infection_time += 1
                # Infect nearby susceptible agents
                for other in self.agents:
                    if other.state == 'S' and agent.distance_to(other) < self.infection_radius:
                        if random.random() < self.infection_prob:
                            other.state = 'I'
                # After recovery_time, decide recovery or death
                if agent.infection_time >= self.recovery_time:
                    if random.random() < self.mortality_prob:
                        agent.state = 'D'
                    elif random.random() < self.recovery_prob:
                        agent.state = 'R'

        # Record simulation state
        self.history.append({
            "time": self.time,
            "aggregate": self.get_aggregate_counts(),
            "agents": [
                {
                    "id": a.agent_id, "lat": a.lat, "lng": a.lng, "state": a.state,
                    "age": a.age, "occupation": a.occupation, "income": a.income
                } for a in self.agents
            ],
            "lockdown": self.lockdown
        })

    def get_aggregate_counts(self):
        counts = {"S": 0, "I": 0, "R": 0, "D": 0}
        for agent in self.agents:
            counts[agent.state] += 1
        return counts

    def get_details(self):
        return {
            "time": self.time,
            "aggregate": self.get_aggregate_counts(),
            "agents": [
                {
                    "id": a.agent_id, "lat": a.lat, "lng": a.lng, "state": a.state,
                    "age": a.age, "occupation": a.occupation, "income": a.income
                } for a in self.agents
            ],
            "lockdown": self.lockdown
        }
