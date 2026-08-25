<div align="center">

# KenkoMirai API

### Versioned simulation sessions with reproducible inputs

<p>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-API-101815?style=for-the-badge&logo=fastapi&logoColor=B8E7D1">
  <img alt="Mesa" src="https://img.shields.io/badge/Mesa-Agent_Lifecycle-101815?style=for-the-badge&labelColor=101815&color=477A65">
  <img alt="SEIRD model" src="https://img.shields.io/badge/Model-SEIRD-101815?style=for-the-badge&labelColor=101815&color=365D4D">
</p>

<p>
  <a href="../README.md"><img alt="Project overview" src="https://img.shields.io/badge/BACK-PROJECT_OVERVIEW-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
  <a href="../docs/architecture.md"><img alt="Architecture" src="https://img.shields.io/badge/VIEW-ARCHITECTURE-B8E7D1?style=for-the-badge&labelColor=101815&color=477A65"></a>
  <a href="../docs/technology.md"><img alt="Technology stack" src="https://img.shields.io/badge/VIEW-TECHNOLOGY-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
</p>

</div>

---

The canonical backend is a FastAPI service around a Mesa 3 `Model`/`Agent` simulation, deterministic hourly SEIRD transitions, validated mobility resources, population-weighted census tract geography, and a bounded interactive-session manager.

```bash
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
python -m pytest tests
```

Use `/api/v1` for new integrations. API documentation is served at `/docs`. A multi-step advance returns both the final `snapshot` and every generated `history` sample; paginated recovery is available at `/api/v1/simulations/{id}/history`. Interactive sessions are process-local, so run one worker; use `/api/v1/simulations/run` for stateless batch execution.

Startup fails if configured mobility or geography inputs are absent or invalid. Heavy requests are rejected with `429` when the bounded compute gate is occupied, and with `422` when work or lifetime limits are exceeded.

See [architecture](../docs/architecture.md) and [setup](../docs/setup.md).
