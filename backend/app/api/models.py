from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PolicyAction(str, Enum):
    open = "open"
    lockdown = "lockdown"
    adaptive = "adaptive"


class AgentState(BaseModel):
    id: int = Field(ge=0)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    state: Literal["S", "E", "I", "R", "D"]
    age: int = Field(ge=0, le=120)
    occupation: str
    income: str


class SimulationSummary(BaseModel):
    time: int = Field(ge=0)
    elapsed_days: float = Field(ge=0)
    hour_of_day: int = Field(ge=0, le=23)
    aggregate: dict[str, int]
    lockdown: bool
    active_policy: PolicyAction
    new_exposures: int = Field(ge=0)
    new_infectious: int = Field(ge=0)
    new_recoveries: int = Field(ge=0)
    new_deaths: int = Field(ge=0)
    exposure_ratio: float = Field(ge=0)
    mobility_multiplier: float = Field(ge=0, le=2)
    mobility_date: str | None

    @model_validator(mode="after")
    def validate_aggregate(self) -> "SimulationSummary":
        if set(self.aggregate) != {"S", "E", "I", "R", "D"}:
            raise ValueError("aggregate must contain exactly S, E, I, R, and D")
        if any(value < 0 for value in self.aggregate.values()):
            raise ValueError("aggregate counts cannot be negative")
        return self


class SimulationSnapshot(SimulationSummary):
    simulation_id: str
    agents: list[AgentState]


class SimulationAdvanceResult(BaseModel):
    snapshot: SimulationSnapshot
    history: list[SimulationSummary]


class SimulationHistoryPage(BaseModel):
    simulation_id: str
    items: list[SimulationSummary]
    next_after: int = Field(ge=-1)
    has_more: bool


class ResourceMetadata(BaseModel):
    mobility_source: str
    geography_source: str
    mobility_records: int = Field(gt=0)
    population_centers: int = Field(gt=0)
    represented_population: int = Field(gt=0)
    fingerprint: str


class SimulationResult(BaseModel):
    simulation_id: str
    seed: int
    model_version: str
    resources: ResourceMetadata
    configuration: dict[str, object]
    final: SimulationSnapshot
    history: list[SimulationSummary]


class SimulationCreateRequest(BaseModel):
    num_agents: int | None = Field(default=None, ge=10)
    initial_infected: int | None = Field(default=None, ge=0)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)
    policy: PolicyAction = PolicyAction.open

    @model_validator(mode="after")
    def validate_initial_infected(self) -> "SimulationCreateRequest":
        if self.initial_infected is not None and self.num_agents is not None and self.initial_infected > self.num_agents:
            raise ValueError("initial_infected cannot exceed num_agents")
        return self


class SimulationAdvanceRequest(BaseModel):
    steps: int = Field(default=1, ge=1)
    policy: PolicyAction | None = None


class SimulationRunRequest(SimulationCreateRequest):
    steps: int | None = Field(default=None, ge=1)
    include_agents: bool = True


class SessionCreated(BaseModel):
    simulation_id: str
    seed: int
    resources: ResourceMetadata
    configuration: dict[str, object]
    snapshot: SimulationSnapshot


class ServiceLimits(BaseModel):
    max_agents: int = Field(gt=0)
    max_steps_per_request: int = Field(gt=0)
    max_total_steps_per_session: int = Field(gt=0)
    max_sessions: int = Field(gt=0)
    max_retained_agents: int = Field(gt=0)


class ServiceHealth(BaseModel):
    status: Literal["ok", "ready"]
    service: str
    version: str
    environment: str
    active_sessions: int = Field(ge=0)
    resource_fingerprint: str
    limits: ServiceLimits


class ErrorResponse(BaseModel):
    detail: str
    request_id: str | None = None
