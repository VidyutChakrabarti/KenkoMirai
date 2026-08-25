from __future__ import annotations

from app.simulation.environment import CovidEnvironment


def simulate_rl_decision(env_state: dict[str, object], *, currently_locked_down: bool = False) -> str:
    """Conservative fallback policy with hysteresis.

    A trained policy can replace this controller at deployment time. Calling it RL
    would be misleading until a compatible checkpoint is supplied and validated.
    """
    aggregate = env_state.get("aggregate", {})
    if not isinstance(aggregate, dict):
        raise ValueError("env_state.aggregate must be an object")
    total = sum(int(value) for value in aggregate.values())
    infected = int(aggregate.get("I", 0))
    if total <= 0:
        return "open"
    threshold = 0.04 if currently_locked_down else 0.10
    return "lockdown" if infected / total >= threshold else "open"


def apply_rl_decision(environment: CovidEnvironment, decision: str) -> CovidEnvironment:
    environment.set_policy(decision)
    return environment
