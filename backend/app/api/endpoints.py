from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, Response, status

from app.api import models
from app.config import Settings
from app.simulation.manager import (
    SessionCapacityError,
    SessionNotFoundError,
    SimulationBusyError,
    SimulationManager,
)


router = APIRouter(prefix="/api/v1")
compatibility_router = APIRouter()


def _services(request: Request) -> tuple[SimulationManager, Settings]:
    return request.app.state.simulation_manager, request.app.state.settings


def _not_found(simulation_id: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"simulation session {simulation_id!r} was not found or expired")


def _limits(settings: Settings) -> models.ServiceLimits:
    return models.ServiceLimits(
        max_agents=settings.max_agents,
        max_steps_per_request=settings.max_steps_per_request,
        max_total_steps_per_session=settings.max_total_steps_per_session,
        max_sessions=settings.max_sessions,
        max_retained_agents=settings.max_retained_agents,
    )


@router.get("/health", response_model=models.ServiceHealth, tags=["operations"])
def health(request: Request) -> models.ServiceHealth:
    manager, settings = _services(request)
    return models.ServiceHealth(
        status="ok",
        service="kenkomirai-api",
        version=request.app.version,
        environment=settings.environment,
        active_sessions=manager.count(),
        resource_fingerprint=manager.resources.fingerprint,
        limits=_limits(settings),
    )


@router.get("/ready", response_model=models.ServiceHealth, tags=["operations"])
def readiness(request: Request) -> models.ServiceHealth:
    manager, settings = _services(request)
    return models.ServiceHealth(
        status="ready",
        service="kenkomirai-api",
        version=request.app.version,
        environment=settings.environment,
        active_sessions=manager.count(),
        resource_fingerprint=manager.resources.fingerprint,
        limits=_limits(settings),
    )


@router.post(
    "/simulations",
    response_model=models.SessionCreated,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": models.ErrorResponse}, 429: {"model": models.ErrorResponse}},
    tags=["simulations"],
)
def create_simulation(payload: models.SimulationCreateRequest, request: Request) -> models.SessionCreated:
    manager, settings = _services(request)
    seed = settings.default_seed if payload.seed is None else payload.seed
    num_agents = settings.default_agents if payload.num_agents is None else payload.num_agents
    initial_infected = min(20, num_agents) if payload.initial_infected is None else payload.initial_infected
    try:
        simulation_id, environment = manager.create(
            num_agents=num_agents,
            initial_infected=initial_infected,
            seed=seed,
            policy=payload.policy.value,
        )
    except SessionCapacityError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SimulationBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    snapshot = {"simulation_id": simulation_id, **environment.get_details()}
    return models.SessionCreated(
        simulation_id=simulation_id,
        seed=seed,
        resources=models.ResourceMetadata.model_validate(manager.resources.metadata()),
        configuration=environment.configuration(),
        snapshot=snapshot,
    )


@router.get(
    "/simulations/{simulation_id}",
    response_model=models.SimulationSnapshot,
    responses={404: {"model": models.ErrorResponse}},
    tags=["simulations"],
)
def get_simulation(simulation_id: str, request: Request, include_agents: bool = True) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.snapshot(simulation_id, include_agents=include_agents)
    except SessionNotFoundError as exc:
        raise _not_found(simulation_id) from exc


@router.get(
    "/simulations/{simulation_id}/history",
    response_model=models.SimulationHistoryPage,
    responses={404: {"model": models.ErrorResponse}},
    tags=["simulations"],
)
def get_simulation_history(
    simulation_id: str,
    request: Request,
    after: int = Query(default=-1, ge=-1),
    limit: int = Query(default=1_000, ge=1, le=1_000),
) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.history(simulation_id, after=after, limit=limit)
    except SessionNotFoundError as exc:
        raise _not_found(simulation_id) from exc


@router.post(
    "/simulations/{simulation_id}/steps",
    response_model=models.SimulationAdvanceResult,
    responses={404: {"model": models.ErrorResponse}, 429: {"model": models.ErrorResponse}},
    tags=["simulations"],
)
def advance_simulation(
    simulation_id: str,
    payload: models.SimulationAdvanceRequest,
    request: Request,
    include_agents: bool = True,
) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.advance(
            simulation_id,
            steps=payload.steps,
            policy=payload.policy.value if payload.policy else None,
            include_agents=include_agents,
        )
    except SessionNotFoundError as exc:
        raise _not_found(simulation_id) from exc
    except SimulationBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete(
    "/simulations/{simulation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": models.ErrorResponse}},
    tags=["simulations"],
)
def delete_simulation(simulation_id: str, request: Request) -> Response:
    manager, _ = _services(request)
    try:
        manager.delete(simulation_id)
    except SessionNotFoundError as exc:
        raise _not_found(simulation_id) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/simulations/run", response_model=models.SimulationResult, tags=["simulations"])
def run_batch(payload: models.SimulationRunRequest, request: Request) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.run_batch(
            steps=payload.steps,
            num_agents=payload.num_agents,
            initial_infected=payload.initial_infected,
            seed=payload.seed,
            policy=payload.policy.value,
            include_agents=payload.include_agents,
        )
    except SimulationBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@compatibility_router.get("/health", deprecated=True, include_in_schema=False)
def legacy_health(_request: Request) -> dict[str, str]:
    return {"status": "ok"}


@compatibility_router.get("/simulation", response_model=models.SimulationResult, deprecated=True, tags=["compatibility"])
def legacy_simulation(
    request: Request,
    steps: int = Query(default=168, ge=1),
    num_agents: int = Query(default=500, ge=10),
    initial_infected: int = Query(default=20, ge=0),
    seed: int | None = Query(default=None, ge=0),
    policy: models.PolicyAction = models.PolicyAction.open,
) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.run_batch(
            steps=steps,
            num_agents=num_agents,
            initial_infected=initial_infected,
            seed=seed,
            policy=policy.value,
        )
    except SimulationBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@compatibility_router.post("/simulate-step", response_model=models.SimulationResult, deprecated=True, tags=["compatibility"])
def legacy_simulation_step(request: Request, apply_rl: bool = False) -> dict[str, object]:
    manager, _ = _services(request)
    try:
        return manager.run_batch(steps=1, policy="adaptive" if apply_rl else "open")
    except SimulationBusyError as exc:
        raise HTTPException(status_code=429, detail=str(exc), headers={"Retry-After": "1"}) from exc
