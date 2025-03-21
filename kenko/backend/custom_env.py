import gym
from gym import spaces
import numpy as np
from simulation import LASimulation

class LAEnv(gym.Env):
    """
    Custom Gym environment for LA COVID simulation.
    Observation: For each neighborhood, infection rate and economic loss plus one travel flag.
    Action: A MultiDiscrete space with two components:
      - action_type: 0 = no-op, 1 = toggle lockdown (apply/lift), 2 = toggle travel restriction.
      - target: neighborhood index (used only for action_type 1).
    """
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super(LAEnv, self).__init__()
        self.sim = LASimulation()
        self.num_neighborhoods = len(self.sim.neighborhoods)
        low = np.zeros(self.num_neighborhoods * 2 + 1)
        high = np.ones(self.num_neighborhoods * 2 + 1)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)
        self.action_space = spaces.MultiDiscrete([3, self.num_neighborhoods])

    def step(self, action):
        action_type_index, target_index = action
        neighborhood_keys = sorted(self.sim.neighborhoods.keys())
        target = neighborhood_keys[target_index]
        if action_type_index == 0:
            rl_action = {"action_type": "none", "target": None}
        elif action_type_index == 1:
            if self.sim.lockdowns[target]:
                rl_action = {"action_type": "lift_lockdown", "target": target}
            else:
                rl_action = {"action_type": "lockdown", "target": target}
        elif action_type_index == 2:
            if self.sim.travel_restricted:
                rl_action = {"action_type": "lift_travel", "target": None}
            else:
                rl_action = {"action_type": "restrict_travel", "target": None}
        else:
            rl_action = {"action_type": "none", "target": None}
        
        self.sim.apply_rl_action(rl_action)
        self.sim.update_simulation()

        infection = np.array([self.sim.infection_rates[n] for n in sorted(self.sim.neighborhoods.keys())])
        econ = np.array([min(self.sim.economic_loss[n], 1.0) for n in sorted(self.sim.neighborhoods.keys())])
        travel_flag = np.array([1.0]) if self.sim.travel_restricted else np.array([0.0])
        observation = np.concatenate([infection, econ, travel_flag]).astype(np.float32)
        reward = - (np.sum(infection) * 2 + np.sum(econ))
        done = self.sim.time_step >= 50
        info = {"timeStep": self.sim.time_step}
        return observation, reward, done, info

    def reset(self):
        self.sim.reset_simulation()
        infection = np.array([self.sim.infection_rates[n] for n in sorted(self.sim.neighborhoods.keys())])
        econ = np.array([min(self.sim.economic_loss[n], 1.0) for n in sorted(self.sim.neighborhoods.keys())])
        travel_flag = np.array([1.0]) if self.sim.travel_restricted else np.array([0.0])
        observation = np.concatenate([infection, econ, travel_flag]).astype(np.float32)
        return observation

    def render(self, mode='human'):
        print("Time step:", self.sim.time_step)
        print("Infection rates:", self.sim.infection_rates)
        print("Economic loss:", self.sim.economic_loss)
