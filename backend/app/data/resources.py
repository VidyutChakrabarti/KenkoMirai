from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import shapefile

from app.data.ingest import DEFAULT_CONFIG, DatasetValidationError, ingest_data, load_config, resolve_path
from app.data.preprocess import MOBILITY_FIELDS, preprocess_data


NON_RESIDENTIAL_FIELDS = MOBILITY_FIELDS[:-1]
LA_SCENARIO_BOUNDS = (33.65, 34.85, -118.95, -117.60)
US_SURVEY_FOOT_METERS = 0.304800609601219
GRS80_SEMI_MAJOR_METERS = 6_378_137.0
GRS80_INVERSE_FLATTENING = 298.257222101
STATE_PLANE_FALSE_EASTING_FEET = 6_561_666.667
STATE_PLANE_FALSE_NORTHING_FEET = 1_640_416.667
STATE_PLANE_CENTRAL_MERIDIAN = -118.0
STATE_PLANE_LATITUDE_OF_ORIGIN = 33.5
STATE_PLANE_STANDARD_PARALLELS = (35.4666666666667, 34.0333333333333)


@dataclass(frozen=True, slots=True)
class SimulationResources:
    population_centers: tuple[tuple[float, float], ...]
    population_weights: tuple[float, ...]
    mobility_multipliers: tuple[float, ...]
    mobility_dates: tuple[str, ...]
    mobility_source: str
    geography_source: str
    fingerprint: str

    def metadata(self) -> dict[str, object]:
        return {
            "mobility_source": Path(self.mobility_source).name,
            "geography_source": Path(self.geography_source).name,
            "mobility_records": len(self.mobility_multipliers),
            "population_centers": len(self.population_centers),
            "represented_population": int(sum(self.population_weights)),
            "fingerprint": self.fingerprint,
        }


def _state_plane_to_wgs84(easting_feet: float, northing_feet: float) -> tuple[float, float]:
    flattening = 1 / GRS80_INVERSE_FLATTENING
    eccentricity = math.sqrt(flattening * (2 - flattening))

    def m(latitude: float) -> float:
        return math.cos(latitude) / math.sqrt(1 - eccentricity**2 * math.sin(latitude) ** 2)

    def t(latitude: float) -> float:
        ratio = (1 - eccentricity * math.sin(latitude)) / (1 + eccentricity * math.sin(latitude))
        return math.tan(math.pi / 4 - latitude / 2) / ratio ** (eccentricity / 2)

    first_parallel, second_parallel = (math.radians(value) for value in STATE_PLANE_STANDARD_PARALLELS)
    origin_latitude = math.radians(STATE_PLANE_LATITUDE_OF_ORIGIN)
    central_meridian = math.radians(STATE_PLANE_CENTRAL_MERIDIAN)
    cone = math.log(m(first_parallel) / m(second_parallel)) / math.log(t(first_parallel) / t(second_parallel))
    scale = m(first_parallel) / (cone * t(first_parallel) ** cone)
    origin_radius = GRS80_SEMI_MAJOR_METERS * scale * t(origin_latitude) ** cone

    delta_easting = (easting_feet - STATE_PLANE_FALSE_EASTING_FEET) * US_SURVEY_FOOT_METERS
    delta_northing = (northing_feet - STATE_PLANE_FALSE_NORTHING_FEET) * US_SURVEY_FOOT_METERS
    adjusted_northing = origin_radius - delta_northing
    radius = math.copysign(math.hypot(delta_easting, adjusted_northing), cone)
    angle = math.atan2(delta_easting, adjusted_northing)
    projected_t = (radius / (GRS80_SEMI_MAJOR_METERS * scale)) ** (1 / cone)
    latitude = math.pi / 2 - 2 * math.atan(projected_t)
    for _ in range(12):
        ratio = (1 - eccentricity * math.sin(latitude)) / (1 + eccentricity * math.sin(latitude))
        updated = math.pi / 2 - 2 * math.atan(projected_t * ratio ** (eccentricity / 2))
        if abs(updated - latitude) < 1e-12:
            latitude = updated
            break
        latitude = updated
    longitude = central_meridian + angle / cone
    return math.degrees(latitude), math.degrees(longitude)


def load_weighted_population_centers(path: Path) -> tuple[tuple[tuple[float, float], ...], tuple[float, ...]]:
    projection = path.with_suffix(".prj")
    if not projection.is_file():
        raise DatasetValidationError("population shapefile requires a matching .prj file")
    projection_text = projection.read_text(encoding="utf-8-sig")
    if "NAD_1983_StatePlane_California_V_FIPS_0405_Feet" not in projection_text:
        raise DatasetValidationError("population shapefile projection is not the supported California State Plane V feet CRS")
    try:
        reader = shapefile.Reader(str(path))
    except shapefile.ShapefileException as exc:
        raise DatasetValidationError(f"cannot read population shapefile: {path}") from exc
    centers: list[tuple[float, float]] = []
    weights: list[float] = []
    try:
        field_names = [str(field[0]) for field in reader.fields[1:]]
        population_field = next((name for name in field_names if name.upper() == "POP20_TOTA"), None)
        if population_field is None:
            raise DatasetValidationError("population shapefile is missing POP20_TOTA")
        population_index = field_names.index(population_field)
        for item in reader.iterShapeRecords():
            if len(item.shape.bbox) != 4:
                continue
            min_easting, min_northing, max_easting, max_northing = (
                float(value) for value in item.shape.bbox
            )
            population = float(item.record[population_index] or 0)
            if population <= 0:
                continue
            latitude, longitude = _state_plane_to_wgs84(
                (min_easting + max_easting) / 2,
                (min_northing + max_northing) / 2,
            )
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise DatasetValidationError("population shapefile contains an out-of-range bounding box")
            lower_lat, upper_lat, lower_lng, upper_lng = LA_SCENARIO_BOUNDS
            if not (lower_lat <= latitude <= upper_lat and lower_lng <= longitude <= upper_lng):
                continue
            centers.append((latitude, longitude))
            weights.append(population)
    finally:
        reader.close()
    if not centers:
        raise DatasetValidationError("population shapefile contains no populated areas")
    return tuple(centers), tuple(weights)


def _mobility_profile(records: list[dict[str, object]]) -> tuple[tuple[float, ...], tuple[str, ...]]:
    multipliers: list[float] = []
    dates: list[str] = []
    for record in records:
        values = [float(record[field]) for field in NON_RESIDENTIAL_FIELDS if record[field] is not None]
        average_change = sum(values) / len(values) if values else 0.0
        # The Google-style percentage deltas describe activity relative to baseline.
        # Bound them so anomalous source rows cannot stop movement or amplify it without limit.
        multipliers.append(round(min(1.35, max(0.25, 1.0 + average_change / 100.0)), 4))
        dates.append(str(record["date"]))
    return tuple(multipliers), tuple(dates)


def load_simulation_resources(config_path: str | Path = DEFAULT_CONFIG) -> SimulationResources:
    config_file, config = load_config(config_path)
    configured_population = config.get("population_shapefile")
    if not isinstance(configured_population, str) or not configured_population.strip():
        raise DatasetValidationError("population_shapefile must be configured")
    population_shapefile = resolve_path(
        config_file,
        configured_population,
        environment_name="KENKOMIRAI_POPULATION_SHAPEFILE",
    )
    mobility = ingest_data(config_file)
    prepared = preprocess_data(mobility["records"])
    multipliers, dates = _mobility_profile(prepared)
    if not multipliers:
        raise DatasetValidationError("mobility profile contains no usable records")
    centers, weights = load_weighted_population_centers(population_shapefile)
    digest = hashlib.sha256()
    shapefile_base = population_shapefile.with_suffix("")
    population_files = [shapefile_base.with_suffix(suffix) for suffix in (".shp", ".shx", ".dbf", ".prj")]
    if any(not source.is_file() for source in population_files):
        raise DatasetValidationError("population shapefile requires matching .shp, .shx, .dbf, and .prj files")
    for source in (Path(str(mobility["source"])), *population_files):
        digest.update(source.read_bytes())
    return SimulationResources(
        population_centers=centers,
        population_weights=weights,
        mobility_multipliers=multipliers,
        mobility_dates=dates,
        mobility_source=str(mobility["source"]),
        geography_source=str(population_shapefile),
        fingerprint=digest.hexdigest()[:16],
    )
