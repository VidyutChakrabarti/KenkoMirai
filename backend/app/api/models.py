from pydantic import BaseModel
from typing import List, Dict

class AgentState(BaseModel):
    id: int
    lat: float
    lng: float
    state: str
    age: int
    occupation: str
    income: str

class SimulationStep(BaseModel):
    time: int
    aggregate: Dict[str, int]  # e.g., {"S": 450, "I": 30, "R": 15, "D": 5}
    agents: List[AgentState]
    lockdown: bool

class SimulationResult(BaseModel):
    final: SimulationStep
    history: List[SimulationStep]
