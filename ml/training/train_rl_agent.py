import os
import sys
import gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

# Ensure the backend directory is in the Python path
sys.path.append('../backend')
from app.simulation.gym_env import CovidGymEnv

def train_rl_agent(total_timesteps=10000):
    env = CovidGymEnv()
    check_env(env, warn=True)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=total_timesteps)
    os.makedirs("models", exist_ok=True)
    model.save("models/ppo_covid")
    return model

if __name__ == "__main__":
    model = train_rl_agent(total_timesteps=50000)
    print("RL Agent training complete. Model saved to models/ppo_covid")
