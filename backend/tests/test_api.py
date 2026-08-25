from fastapi.testclient import TestClient

from app.main import app


def test_health_and_session_lifecycle() -> None:
    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert len(health.json()["resource_fingerprint"]) == 16

        created = client.post(
            "/api/v1/simulations",
            json={"num_agents": 50, "initial_infected": 3, "seed": 7, "policy": "adaptive"},
        )
        assert created.status_code == 201
        simulation_id = created.json()["simulation_id"]

        advanced = client.post(
            f"/api/v1/simulations/{simulation_id}/steps",
            json={"steps": 2, "policy": "adaptive"},
        )
        assert advanced.status_code == 200
        assert advanced.json()["snapshot"]["time"] == 2
        assert [item["time"] for item in advanced.json()["history"]] == [1, 2]

        history = client.get(f"/api/v1/simulations/{simulation_id}/history", params={"after": 0})
        assert history.status_code == 200
        assert [item["time"] for item in history.json()["items"]] == [1, 2]

        deleted = client.delete(f"/api/v1/simulations/{simulation_id}")
        assert deleted.status_code == 204
        assert client.get(f"/api/v1/simulations/{simulation_id}").status_code == 404


def test_rejects_invalid_population() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/simulations",
            json={"num_agents": 20, "initial_infected": 21, "seed": 1},
        )
        assert response.status_code == 422


def test_batch_result_identifies_model_inputs() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/simulations/run",
            json={"num_agents": 20, "initial_infected": 2, "steps": 2, "seed": 11},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["model_version"] == "mesa-seird-agent-v2"
        assert payload["resources"]["mobility_records"] > 0
        assert payload["resources"]["represented_population"] > 1_000_000
        assert payload["configuration"]["time_unit"] == "hour"
        assert len(payload["history"]) == 3
