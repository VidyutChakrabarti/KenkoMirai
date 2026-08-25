from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _integer(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _floating(name: str, default: float, *, minimum: float, maximum: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _csv(name: str, default: str) -> tuple[str, ...]:
    values = tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())
    if not values:
        raise ValueError(f"{name} must contain at least one value")
    return values


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    environment: str
    api_prefix: str
    log_level: str
    cors_origins: tuple[str, ...]
    allowed_hosts: tuple[str, ...]
    default_agents: int
    max_agents: int
    default_steps: int
    max_steps_per_request: int
    max_total_steps_per_session: int
    max_work_units: int
    max_concurrent_runs: int
    max_sessions: int
    max_retained_agents: int
    session_ttl_seconds: int
    default_seed: int
    infection_radius_km: float
    transmission_probability: float
    incubation_steps: int
    infectious_steps: int
    base_mortality_probability: float
    lockdown_mobility_factor: float

    @classmethod
    def from_environment(cls) -> "Settings":
        environment = os.getenv("KENKOMIRAI_ENVIRONMENT", "development").strip().lower()
        if environment not in {"development", "test", "production"}:
            raise ValueError("KENKOMIRAI_ENVIRONMENT must be development, test, or production")
        log_level = os.getenv("KENKOMIRAI_LOG_LEVEL", "INFO").strip().upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("KENKOMIRAI_LOG_LEVEL is invalid")
        settings = cls(
            app_name="KenkoMirai Simulation API",
            environment=environment,
            api_prefix="/api/v1",
            log_level=log_level,
            cors_origins=_csv("KENKOMIRAI_CORS_ORIGINS", "http://localhost:3000"),
            allowed_hosts=_csv("KENKOMIRAI_ALLOWED_HOSTS", "localhost,127.0.0.1,backend,testserver"),
            default_agents=_integer("KENKOMIRAI_DEFAULT_AGENTS", 500, minimum=10, maximum=50_000),
            max_agents=_integer("KENKOMIRAI_MAX_AGENTS", 10_000, minimum=10, maximum=100_000),
            default_steps=_integer("KENKOMIRAI_DEFAULT_STEPS", 168, minimum=1, maximum=10_000),
            max_steps_per_request=_integer("KENKOMIRAI_MAX_STEPS_PER_REQUEST", 720, minimum=1, maximum=10_000),
            max_total_steps_per_session=_integer("KENKOMIRAI_MAX_TOTAL_STEPS_PER_SESSION", 10_000, minimum=1, maximum=1_000_000),
            max_work_units=_integer("KENKOMIRAI_MAX_WORK_UNITS", 2_500_000, minimum=10, maximum=100_000_000),
            max_concurrent_runs=_integer("KENKOMIRAI_MAX_CONCURRENT_RUNS", 2, minimum=1, maximum=128),
            max_sessions=_integer("KENKOMIRAI_MAX_SESSIONS", 64, minimum=1, maximum=10_000),
            max_retained_agents=_integer("KENKOMIRAI_MAX_RETAINED_AGENTS", 50_000, minimum=10, maximum=1_000_000),
            session_ttl_seconds=_integer("KENKOMIRAI_SESSION_TTL_SECONDS", 3600, minimum=60, maximum=604_800),
            default_seed=_integer("KENKOMIRAI_DEFAULT_SEED", 2025, minimum=0, maximum=2_147_483_647),
            infection_radius_km=_floating("KENKOMIRAI_INFECTION_RADIUS_KM", 0.18, minimum=0.01, maximum=5.0),
            transmission_probability=_floating("KENKOMIRAI_TRANSMISSION_PROBABILITY", 0.08, minimum=0.0, maximum=1.0),
            incubation_steps=_integer("KENKOMIRAI_INCUBATION_STEPS", 72, minimum=1, maximum=2_400),
            infectious_steps=_integer("KENKOMIRAI_INFECTIOUS_STEPS", 240, minimum=1, maximum=8_760),
            base_mortality_probability=_floating("KENKOMIRAI_BASE_MORTALITY", 0.006, minimum=0.0, maximum=1.0),
            lockdown_mobility_factor=_floating("KENKOMIRAI_LOCKDOWN_MOBILITY_FACTOR", 0.22, minimum=0.0, maximum=1.0),
        )
        if settings.default_agents > settings.max_agents:
            raise ValueError("KENKOMIRAI_DEFAULT_AGENTS cannot exceed KENKOMIRAI_MAX_AGENTS")
        if settings.default_steps > settings.max_steps_per_request:
            raise ValueError("KENKOMIRAI_DEFAULT_STEPS cannot exceed KENKOMIRAI_MAX_STEPS_PER_REQUEST")
        if settings.max_steps_per_request > settings.max_total_steps_per_session:
            raise ValueError("KENKOMIRAI_MAX_STEPS_PER_REQUEST cannot exceed KENKOMIRAI_MAX_TOTAL_STEPS_PER_SESSION")
        if settings.max_retained_agents < settings.default_agents:
            raise ValueError("KENKOMIRAI_MAX_RETAINED_AGENTS cannot be lower than KENKOMIRAI_DEFAULT_AGENTS")
        if settings.max_work_units < settings.max_agents:
            raise ValueError("KENKOMIRAI_MAX_WORK_UNITS must allow at least one step at KENKOMIRAI_MAX_AGENTS")
        if settings.default_agents * settings.default_steps > settings.max_work_units:
            raise ValueError("default agents multiplied by default steps exceeds KENKOMIRAI_MAX_WORK_UNITS")
        if max(settings.incubation_steps, settings.infectious_steps) > settings.max_total_steps_per_session:
            raise ValueError("disease durations cannot exceed KENKOMIRAI_MAX_TOTAL_STEPS_PER_SESSION")
        return settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_environment()
