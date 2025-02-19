def simulate_rl_decision(env_state):
    """
    if infected fraction > 15%, trigger lockdown.
    """
    aggregate = env_state.get("aggregate", {})
    total = sum(aggregate.values())
    infected = aggregate.get("I", 0)
    if total > 0 and (infected / total) > 0.15:
        return "lockdown"
    return "open"

def apply_rl_decision(env, decision):
    env.lockdown = True if decision == "lockdown" else False
    return env
