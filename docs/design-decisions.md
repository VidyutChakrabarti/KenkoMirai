# Design decisions

## Mesa for model and agent lifecycle

The supported environment subclasses Mesa `Model`; simulated people subclass Mesa `Agent`. Mesa provides seeded model randomness, automatic registration, lifecycle removal, and `AgentSet.do` activation. Geographic candidate lookup and SEIRD transitions stay in the domain layer because they require exact distance checks and simultaneous commits rather than a generic grid scheduler.

## Reproducibility over opaque realism

All stochastic behavior uses a per-environment `random.Random` instance. Daily routines are transparent templates rather than generated reasoning traces. This makes results reproducible, inspectable, and safer to compare.

## SEIRD rather than SIRD

An exposed state prevents agents from becoming infectious in the same step as contact. State changes are committed simultaneously, eliminating iteration-order artifacts.

## Spatial cells plus exact distance

The simulator uses latitude/longitude cells to find candidate contacts, then haversine distance to validate them. This avoids the old all-pairs scan while retaining a clear physical radius.

## One explicit time unit

One step represents one hour. Routine destinations therefore use hour-of-day directly, mobility CSV rows advance once per 24 steps, and incubation/infectious settings are expressed in hourly steps. API summaries include raw steps, elapsed days, and hour of day.

## Validated, fingerprinted inputs

Mobility and the complete census shapefile set load once when the service starts. Invalid schemas, coordinates, dates, missing shapefile sidecars, unsupported projections, or absent population weights fail startup rather than silently falling back. Batch metadata and health responses expose a short content fingerprint so runs can be associated with the exact packaged inputs.

## Hysteresis for the fallback policy

Adaptive control uses separate entry and release thresholds. This prevents lockdown oscillation around a single threshold. The controller is explicitly identified as a heuristic until a validated trained checkpoint is connected.

## Same-origin frontend gateway

Browser requests go through a Next.js API route. The upstream API URL remains server-side and can change at runtime, avoiding hard-coded localhost values and broad browser CORS.

## SVG visualization

The canonical UI uses React-rendered SVG maps and charts. This avoids missing Leaflet assets, tile-provider availability, client-only imports during server rendering, and chart object leaks. Large agent sets are sampled only for point rendering; aggregate metrics always use the complete population.

## Explicit single-replica session service

Interactive state is in memory and bounded. The deployment therefore uses one backend worker and replica. Pretending this is horizontally safe would be worse than making the boundary explicit. Stateless batch execution can be distributed independently.

Within the process, per-session locks preserve ordering, active work cannot be expired or deleted midway, total session steps bound memory growth, and a compute semaphore prevents unbounded heavy-request queues.

## Opt-in training

Compose does not train by default. The Gym adapter shares the API's model parameters and fingerprinted resources. The training profile emits a checkpoint and metadata describing observation order, actions, seed, population, model version, source fingerprint, and format version. Deployment does not load an unvalidated model automatically.
