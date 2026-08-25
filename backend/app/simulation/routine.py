from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RoutineStop:
    hour: int
    latitude: float
    longitude: float
    purpose: str


def _bounded(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def _destination(
    home: tuple[float, float],
    bounds: tuple[float, float, float, float],
    rng: random.Random,
    spread: float,
) -> tuple[float, float]:
    min_lat, max_lat, min_lng, max_lng = bounds
    return (
        _bounded(home[0] + rng.uniform(-spread, spread), min_lat, max_lat),
        _bounded(home[1] + rng.uniform(-spread, spread), min_lng, max_lng),
    )


def build_daily_routine(
    *,
    occupation: str,
    income_band: str,
    home: tuple[float, float],
    bounds: tuple[float, float, float, float],
    rng: random.Random,
) -> tuple[RoutineStop, ...]:
    """Build a transparent schedule template; no hidden model reasoning is used."""
    stops = [RoutineStop(0, home[0], home[1], "home")]
    if occupation in {"student", "office_worker", "healthcare", "service"}:
        commute = _destination(home, bounds, rng, 0.045 if income_band == "high" else 0.028)
        stops.append(RoutineStop(8, commute[0], commute[1], "work_or_school"))
        midday = _destination(commute, bounds, rng, 0.009)
        stops.append(RoutineStop(12, midday[0], midday[1], "midday_errand"))
        stops.append(RoutineStop(13, commute[0], commute[1], "work_or_school"))
    elif occupation == "retired":
        community = _destination(home, bounds, rng, 0.014)
        stops.append(RoutineStop(10, community[0], community[1], "community_activity"))
    else:
        errand = _destination(home, bounds, rng, 0.018)
        stops.append(RoutineStop(11, errand[0], errand[1], "errand"))
    stops.append(RoutineStop(18, home[0], home[1], "home"))
    return tuple(sorted(stops, key=lambda stop: stop.hour))


def destination_for_hour(routine: tuple[RoutineStop, ...], hour: int) -> RoutineStop:
    selected = routine[0]
    for stop in routine:
        if stop.hour > hour:
            break
        selected = stop
    return selected
