# Setup and operations

This guide covers the canonical `backend/`, `frontend/`, and optional `ml/` modules.

## Prerequisites

- Python 3.12
- Node.js 22 and npm
- Docker with Compose v2 for the container path
- `kubectl` for Kubernetes deployment

## Environment

Copy `.env.example` to `.env` and adjust the limits for your environment. The application does not load `.env` implicitly; export the values in your process manager or pass them through Compose/Kubernetes.

Important variables:

| Variable | Default | Purpose |
|---|---:|---|
| `KENKOMIRAI_API_URL` | `http://127.0.0.1:8000` | Server-side Next.js gateway upstream |
| `KENKOMIRAI_MAX_AGENTS` | `10000` | Per-scenario population ceiling |
| `KENKOMIRAI_MAX_STEPS_PER_REQUEST` | `720` | Hourly-step ceiling for one advance request |
| `KENKOMIRAI_MAX_TOTAL_STEPS_PER_SESSION` | `10000` | Retained-history/lifetime ceiling |
| `KENKOMIRAI_MAX_WORK_UNITS` | `2500000` | Maximum agents × steps in one request |
| `KENKOMIRAI_MAX_CONCURRENT_RUNS` | `2` | In-process compute admission slots |
| `KENKOMIRAI_MAX_SESSIONS` | `64` | Retained interactive-session capacity |
| `KENKOMIRAI_MAX_RETAINED_AGENTS` | `50000` | Cross-session retained population budget |
| `KENKOMIRAI_SESSION_TTL_SECONDS` | `3600` | Idle-session expiry |
| `KENKOMIRAI_ALLOWED_HOSTS` | local hosts | FastAPI trusted hosts |
| `KENKOMIRAI_CORS_ORIGINS` | `http://localhost:3000` | Direct API browser origins |
| `KENKOMIRAI_MOBILITY_CSV` | bundled path | Optional absolute mobility-data override |
| `KENKOMIRAI_POPULATION_SHAPEFILE` | bundled path | Optional absolute census `.shp` override; matching `.shx`, `.dbf`, and supported `.prj` are required |
| `KENKOMIRAI_GATEWAY_TIMEOUT_MS` | `120000` | Server-side frontend gateway timeout |

## Docker Compose

```bash
cd infrastructure
docker compose up --build
```

Compose starts the API on port `8000` and the web application on port `3000`. It does not train an RL model.

To run the opt-in trainer and persist the checkpoint in the `model-artifacts` Docker volume:

```bash
docker compose --profile training run --rm trainer
```

## Direct development

Backend:

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, from the repository root:

```bash
npm ci
set KENKOMIRAI_API_URL=http://127.0.0.1:8000
npm run dev
```

On Linux/macOS, use `export` instead of `set`.

## Static quality gates

```bash
python -m pytest backend/tests
npm run lint
npm run build
```

## Kubernetes

Build and publish the two images, then set their registry references with Kustomize:

```bash
cd infrastructure/k8s
kustomize edit set image kenkomirai/backend=registry.example.com/kenkomirai/backend:1.2.0
kustomize edit set image kenkomirai/frontend=registry.example.com/kenkomirai/frontend:1.2.0
```

Update `configmap.yaml`, `ingress.yaml`, and the public hostname. Create the referenced TLS secret (or configure your certificate controller) before exposing the ingress:

```bash
kubectl -n kenkomirai create secret tls kenkomirai-tls --cert=path/to/tls.crt --key=path/to/tls.key
```

Deploy from any working directory:

```bash
./infrastructure/scripts/deploy.sh
```

The frontend has two replicas. The interactive-session backend intentionally has one replica because its bounded session store is process-local. Do not raise backend replicas or worker count until an external session store is implemented.

## Production checklist

- Put the frontend behind TLS and your authentication/authorization layer.
- Replace example image names and public origins.
- Set CPU/memory requests from measured workloads.
- Restrict ingress with your cluster NetworkPolicies.
- Ship stdout logs to centralized storage and propagate `X-Request-ID`.
- Tune compute/work limits from measured latency and reject oversized scenarios at ingress too.
- Prefer `POST /api/v1/simulations/run` for horizontally distributed batch work.
- Treat outputs as model scenarios, not health forecasts.
