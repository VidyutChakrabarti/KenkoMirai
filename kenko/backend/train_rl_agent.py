from custom_env import LAEnv
from stable_baselines3 import PPO
import json

def train_agent():
    env = LAEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=50000)
    model.save("la_rl_agent_model")
    env.sim.reset_simulation()
    obs = env.reset()
    done = False
    full_action_history = []
    day = 1  # Start from Day 1
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, info = env.step(action)
        # Attach day number to each new action step
        for entry in env.sim.action_history:
            entry["day"] = day
            full_action_history.append(entry)
            day += 1  # Increment day for each step

    with open("policy_plan.json", "w") as f:
        json.dump(full_action_history, f, indent=2)
    print("RL agent training complete. Action plan saved to policy_plan.json.")

if __name__ == "__main__":
    train_agent()
