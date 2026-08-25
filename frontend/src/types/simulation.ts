export type DiseaseState = "S" | "E" | "I" | "R" | "D";
export type Policy = "open" | "lockdown" | "adaptive";

export interface AgentState {
  id: number;
  lat: number;
  lng: number;
  state: DiseaseState;
  age: number;
  occupation: string;
  income: string;
}

export interface SimulationSummary {
  time: number;
  elapsed_days: number;
  hour_of_day: number;
  aggregate: Record<DiseaseState, number>;
  lockdown: boolean;
  active_policy: Policy;
  new_exposures: number;
  new_infectious: number;
  new_recoveries: number;
  new_deaths: number;
  exposure_ratio: number;
  mobility_multiplier: number;
  mobility_date: string | null;
}

export interface SimulationSnapshot extends SimulationSummary {
  simulation_id: string;
  agents: AgentState[];
}

export interface SessionCreated {
  simulation_id: string;
  seed: number;
  resources: {
    mobility_source: string;
    geography_source: string;
    mobility_records: number;
    population_centers: number;
    represented_population: number;
    fingerprint: string;
  };
  configuration: Record<string, unknown>;
  snapshot: SimulationSnapshot;
}

export interface SimulationAdvanceResult {
  snapshot: SimulationSnapshot;
  history: SimulationSummary[];
}

export interface SimulationHistoryPage {
  simulation_id: string;
  items: SimulationSummary[];
  next_after: number;
  has_more: boolean;
}

export interface ServiceHealth {
  status: "ok" | "ready";
  service: string;
  version: string;
  environment: string;
  active_sessions: number;
  resource_fingerprint: string;
  limits: {
    max_agents: number;
    max_steps_per_request: number;
    max_total_steps_per_session: number;
    max_sessions: number;
    max_retained_agents: number;
  };
}
