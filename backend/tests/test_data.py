from app.data.resources import _state_plane_to_wgs84, load_simulation_resources


def test_bundled_resources_are_complete_and_bounded() -> None:
    resources = load_simulation_resources()
    assert len(resources.population_centers) > 1_000
    assert len(resources.population_weights) == len(resources.population_centers)
    assert sum(resources.population_weights) > 1_000_000
    assert len(resources.mobility_dates) == len(resources.mobility_multipliers)
    assert all(0.25 <= value <= 1.35 for value in resources.mobility_multipliers)
    assert len(resources.fingerprint) == 16


def test_state_plane_origin_converts_to_configured_geographic_origin() -> None:
    latitude, longitude = _state_plane_to_wgs84(6_561_666.667, 1_640_416.667)
    assert abs(latitude - 33.5) < 1e-9
    assert abs(longitude + 118.0) < 1e-9
