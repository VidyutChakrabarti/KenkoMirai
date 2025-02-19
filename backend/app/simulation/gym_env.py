import gym
from gym import spaces
import numpy as np
from app.simulation.environment import CovidEnvironment

class CovidGymEnv(gym.Env):
    def __init__(self):
        super(CovidGymEnv, self).__init__()
        self.env = CovidEnvironment(num_agents=500, initial_infected=20)
        self.action_space = spaces.Discrete(2)  # 0: open, 1: lockdown
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float32)

    def step(self, action):
        self.env.lockdown = True if action == 1 else False
        self.env.step()
        agg = self.env.get_aggregate_counts()
        obs = np.array([agg.get('S', 0), agg.get('I', 0), agg.get('R', 0), agg.get('D', 0)], dtype=np.float32)
        reward = -agg.get('I', 0)  # Reward lower infections
        done = self.env.time >= 50
        info = {"time": self.env.time}
        return obs, reward, done, info

    def reset(self):
        self.env.reset()
        agg = self.env.get_aggregate_counts()
        obs = np.array([agg.get('S', 0), agg.get('I', 0), agg.get('R', 0), agg.get('D', 0)], dtype=np.float32)
        return obs

    def render(self, mode="human"):
        agg = self.env.get_aggregate_counts()
        print(f"Time: {self.env.time} | S: {agg.get('S', 0)} I: {agg.get('I', 0)} R: {agg.get('R', 0)} D: {agg.get('D', 0)}")
