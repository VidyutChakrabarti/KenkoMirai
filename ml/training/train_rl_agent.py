from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from app.simulation.gym_env import CovidGymEnv


def train_rl_agent(
    *,
    total_timesteps: int,
    output_path: Path,
    seed: int,
    num_agents: int,
    initial_infected: int,
) -> Path:
    if total_timesteps < 1:
        raise ValueError("total_timesteps must be positive")
    if not 0 <= initial_infected <= num_agents:
        raise ValueError("initial_infected must be between zero and num_agents")
    environment = CovidGymEnv(num_agents=num_agents, initial_infected=initial_infected, seed=seed)
    check_env(environment, warn=True)
    model = PPO("MlpPolicy", environment, verbose=1, seed=seed)
    model.learn(total_timesteps=total_timesteps)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(output_path))
    checkpoint_path = output_path if output_path.suffix == ".zip" else Path(f"{output_path}.zip")
    metadata = {
        "format_version": 1,
        "algorithm": "PPO",
        "observation_order": ["S", "E", "I", "R", "D", "lockdown"],
        "actions": {"0": "open", "1": "lockdown"},
        "total_timesteps": total_timesteps,
        "seed": seed,
        "num_agents": num_agents,
        "initial_infected": initial_infected,
        "model_version": "mesa-seird-agent-v2",
        "resource_fingerprint": environment.resources.fingerprint,
        "simulation_configuration": environment.environment.configuration(),
    }
    checkpoint_path.with_suffix(".metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    environment.close()
    return checkpoint_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an opt-in KenkoMirai PPO policy")
    parser.add_argument("--timesteps", type=int, default=50_000)
    parser.add_argument("--output", type=Path, default=REPOSITORY_ROOT / "ml" / "models" / "ppo_seird")
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--agents", type=int, default=500)
    parser.add_argument("--initial-infected", type=int, default=20)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    saved = train_rl_agent(
        total_timesteps=arguments.timesteps,
        output_path=arguments.output,
        seed=arguments.seed,
        num_agents=arguments.agents,
        initial_infected=arguments.initial_infected,
    )
    print(f"Policy saved to {saved}")
