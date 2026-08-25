from __future__ import annotations

import random
from typing import TypedDict

from app.simulation.routine import RoutineStop, build_daily_routine


class AgentProfile(TypedDict):
    age: int
    occupation: str
    income: str
    daily_routine: tuple[RoutineStop, ...]


def generate_agent_profile(
    *,
    home: tuple[float, float],
    bounds: tuple[float, float, float, float],
    rng: random.Random,
) -> AgentProfile:
    age = rng.choices(
        population=[rng.randint(5, 17), rng.randint(18, 39), rng.randint(40, 64), rng.randint(65, 90)],
        weights=[0.18, 0.34, 0.31, 0.17],
        k=1,
    )[0]
    if age < 18:
        occupation = "student"
    elif age >= 67:
        occupation = "retired"
    else:
        occupation = rng.choices(
            ["office_worker", "healthcare", "service", "unemployed"],
            weights=[0.44, 0.10, 0.31, 0.15],
            k=1,
        )[0]
    income = rng.choices(["low", "medium", "high"], weights=[0.34, 0.48, 0.18], k=1)[0]
    return {
        "age": age,
        "occupation": occupation,
        "income": income,
        "daily_routine": build_daily_routine(
            occupation=occupation,
            income_band=income,
            home=home,
            bounds=bounds,
            rng=rng,
        ),
    }
