import random
import numpy as np
from datetime import datetime

class LASimulation:
    def __init__(self, num_people=100, num_neighborhoods=8):
        self.num_people = num_people
        self.num_neighborhoods = num_neighborhoods
        self.time_step = 0

        # Define bounding box for central LA
        self.lat_min = 34.00
        self.lat_max = 34.10
        self.lon_min = -118.30
        self.lon_max = -118.20

        # Create grid intersections (5x5)
        self.num_grid_rows = 5
        self.num_grid_cols = 5
        self.intersections = self.generate_intersections()

        # Divide area into 8 neighborhoods (2 rows x 4 cols)
        self.neighborhoods = self.generate_neighborhoods()

        # Initialize people at random intersections
        self.people = self.generate_people()

        # Simulation state
        self.lockdowns = {n_id: False for n_id in self.neighborhoods.keys()}
        self.travel_restricted = False

        # Initial infection rates and economic loss
        self.infection_rates = {n_id: random.uniform(0.05, 0.15) for n_id in self.neighborhoods.keys()}
        self.economic_loss = {n_id: 0.0 for n_id in self.neighborhoods.keys()}

        # Hospital stats: each neighborhood gets one hospital
        self.hospital_stats = {
            n_id: {
                "forecastShortage": self.calculate_shortage(self.infection_rates[n_id], False),
                "surplus": random.uniform(0.1, 0.3)
            } for n_id in self.neighborhoods.keys()
        }

        # Logs for RL actions and hospital stats snapshots
        self.action_history = []
        self.hospital_history = []

    def generate_intersections(self):
        intersections = []
        lat_steps = np.linspace(self.lat_min, self.lat_max, self.num_grid_rows)
        lon_steps = np.linspace(self.lon_min, self.lon_max, self.num_grid_cols)
        for lat in lat_steps:
            for lon in lon_steps:
                intersections.append((lat, lon))
        return intersections

    def generate_neighborhoods(self):
        neighborhoods = {}
        num_rows = 2
        num_cols = 4
        n_id = 1
        lat_step = (self.lat_max - self.lat_min) / num_rows
        lon_step = (self.lon_max - self.lon_min) / num_cols
        for r in range(num_rows):
            for c in range(num_cols):
                n_name = f"Neighborhood_{n_id}"
                neighborhoods[n_name] = {
                    "lat_min": self.lat_min + r * lat_step,
                    "lat_max": self.lat_min + (r + 1) * lat_step,
                    "lon_min": self.lon_min + c * lon_step,
                    "lon_max": self.lon_min + (c + 1) * lon_step
                }
                n_id += 1
        return neighborhoods

    def generate_people(self):
        people = []
        for i in range(self.num_people):
            start_pos = random.choice(self.intersections)
            person = {
                "id": i,
                "position": list(start_pos),
                "destination": list(random.choice(self.intersections)),
                "speed": random.uniform(0.0001, 0.0003),
                "neighborhood": self.get_neighborhood(start_pos[0], start_pos[1])
            }
            people.append(person)
        return people

    def get_neighborhood(self, lat, lon):
        for n_id, bounds in self.neighborhoods.items():
            if bounds["lat_min"] <= lat <= bounds["lat_max"] and bounds["lon_min"] <= lon <= bounds["lon_max"]:
                return n_id
        return None

    def calculate_shortage(self, infection_rate, lockdown):
        base_shortage = infection_rate * random.uniform(0.8, 1.2)
        if lockdown:
            base_shortage *= 1.5
        return round(min(base_shortage, 1.0), 2)

    def update_people(self):
        for person in self.people:
            current_lat, current_lon = person["position"]
            dest_lat, dest_lon = person["destination"]

            current_nb = self.get_neighborhood(current_lat, current_lon)
            effective_speed = person["speed"]
            if current_nb and self.lockdowns.get(current_nb, False):
                effective_speed *= 0.3

            dest_nb = self.get_neighborhood(dest_lat, dest_lon)
            if self.travel_restricted and current_nb != dest_nb:
                effective_speed *= 0.3

            vector = [dest_lat - current_lat, dest_lon - current_lon]
            distance = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
            if distance < effective_speed or distance == 0:
                new_dest = random.choice(self.intersections)
                person["destination"] = list(new_dest)
                person["position"] = [dest_lat, dest_lon]
                person["neighborhood"] = self.get_neighborhood(dest_lat, dest_lon)
            else:
                move_lat = effective_speed * vector[0] / distance
                move_lon = effective_speed * vector[1] / distance
                person["position"][0] += move_lat
                person["position"][1] += move_lon

    def update_infections(self):
        for n_id, bounds in self.neighborhoods.items():
            count = sum(1 for person in self.people if person["neighborhood"] == n_id)
            current_rate = self.infection_rates[n_id]
            if self.lockdowns[n_id]:
                new_rate = current_rate * 0.95
                self.economic_loss[n_id] += 0.02
            else:
                new_rate = current_rate + 0.001 * count
                self.economic_loss[n_id] += 0.005 * count
            self.infection_rates[n_id] = min(max(new_rate, 0), 1)
            self.hospital_stats[n_id]["forecastShortage"] = self.calculate_shortage(
                self.infection_rates[n_id], self.lockdowns[n_id]
            )

    def update_simulation(self):
        self.time_step += 1
        self.update_people()
        self.update_infections()
        # Record snapshot of hospital stats for timeline
        snapshot = {
            "timeStep": self.time_step,
            "timestamp": datetime.now().isoformat(),
            "hospitalStats": self.hospital_stats.copy()
        }
        self.hospital_history.append(snapshot)

    def apply_rl_action(self, action):
        action_type = action.get("action_type")
        target = action.get("target")
        timestamp = datetime.now().isoformat()
        if action_type == "lockdown" and target in self.neighborhoods:
            self.lockdowns[target] = True
            note = f"{timestamp}: Lockdown applied in {target}."
        elif action_type == "lift_lockdown" and target in self.neighborhoods:
            self.lockdowns[target] = False
            note = f"{timestamp}: Lockdown lifted in {target}."
        elif action_type == "restrict_travel":
            self.travel_restricted = True
            note = f"{timestamp}: Travel restrictions applied."
        elif action_type == "lift_travel":
            self.travel_restricted = False
            note = f"{timestamp}: Travel restrictions lifted."
        else:
            note = f"{timestamp}: No valid action taken."
        self.action_history.append(note)
        return note

    def get_simulation_state(self):
        return {
            "timeStep": self.time_step,
            "people": self.people,
            "neighborhoods": self.neighborhoods,
            "lockdowns": self.lockdowns,
            "travelRestricted": self.travel_restricted,
            "infectionRates": self.infection_rates,
            "economicLoss": self.economic_loss,
            "hospitalStats": self.hospital_stats,
            "actionHistory": self.action_history
        }

    def get_gemini_suggestions(self):
        suggestions = {}
        for n_id, stats in self.hospital_stats.items():
            shortage = stats["forecastShortage"]
            surplus = stats["surplus"]
            if shortage > 0.5:
                # Recommend the hospital with highest surplus
                best_nb = max(self.hospital_stats.items(), key=lambda x: x[1]["surplus"])[0]
                suggestions[n_id] = f"Shortage predicted in {n_id}. Recommend contacting hospital in {best_nb} with surplus."
            else:
                suggestions[n_id] = f"{n_id} operating normally."
        return suggestions

    def reset_simulation(self):
        self.time_step = 0
        self.people = self.generate_people()
        self.lockdowns = {n_id: False for n_id in self.neighborhoods.keys()}
        self.travel_restricted = False
        self.infection_rates = {n_id: random.uniform(0.05, 0.15) for n_id in self.neighborhoods.keys()}
        self.economic_loss = {n_id: 0.0 for n_id in self.neighborhoods.keys()}
        self.hospital_stats = {
            n_id: {
                "forecastShortage": self.calculate_shortage(self.infection_rates[n_id], False),
                "surplus": random.uniform(0.1, 0.3)
            } for n_id in self.neighborhoods.keys()
        }
        self.action_history = []
        self.hospital_history = []
