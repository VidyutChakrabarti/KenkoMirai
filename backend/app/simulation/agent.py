from __future__ import annotations

import math
import random

import mesa

from app.simulation.routine import RoutineStop, destination_for_hour


VALID_STATES = frozenset({"S", "E", "I", "R", "D"})


class Agent(mesa.Agent):
    def __init__(
        self,
        model: mesa.Model,
        *,
        agent_id: int,
        lat: float,
        lng: float,
        home_lat: float,
        home_lng: float,
        state: str,
        age: int,
        occupation: str,
        income: str,
        daily_routine: tuple[RoutineStop, ...],
    ) -> None:
        super().__init__(model)
        if state not in VALID_STATES:
            raise ValueError(f"state must be one of {sorted(VALID_STATES)}")
        self.agent_id = agent_id
        self.lat = lat
        self.lng = lng
        self.home_lat = home_lat
        self.home_lng = home_lng
        self.state = state
        self.age = age
        self.occupation = occupation
        self.income = income
        self.daily_routine = daily_routine
        self.state_time = 0

    def move(
        self,
        *,
        hour: int,
        mobility_factor: float,
        max_move_degrees: float,
        bounds: tuple[float, float, float, float],
        rng: random.Random,
    ) -> None:
        if self.state == "D" or mobility_factor <= 0:
            return
        target = destination_for_hour(self.daily_routine, hour)
        delta_lat = target.latitude - self.lat
        delta_lng = target.longitude - self.lng
        distance = math.hypot(delta_lat, delta_lng)
        max_move = max_move_degrees * mobility_factor
        if distance > 0:
            scale = min(1.0, max_move / distance)
            self.lat += delta_lat * scale
            self.lng += delta_lng * scale
        jitter = max_move * 0.08
        self.lat += rng.uniform(-jitter, jitter)
        self.lng += rng.uniform(-jitter, jitter)
        min_lat, max_lat, min_lng, max_lng = bounds
        self.lat = min(max_lat, max(min_lat, self.lat))
        self.lng = min(max_lng, max(min_lng, self.lng))

    def serialize(self) -> dict[str, int | float | str]:
        return {
            "id": self.agent_id,
            "lat": round(self.lat, 6),
            "lng": round(self.lng, 6),
            "state": self.state,
            "age": self.age,
            "occupation": self.occupation,
            "income": self.income,
        }
