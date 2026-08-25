from __future__ import annotations

from datetime import datetime
import math
from typing import Iterable, Mapping


MOBILITY_FIELDS = (
    "retail_and_recreation_percent_change_from_baseline",
    "grocery_and_pharmacy_percent_change_from_baseline",
    "parks_percent_change_from_baseline",
    "transit_stations_percent_change_from_baseline",
    "workplaces_percent_change_from_baseline",
    "residential_percent_change_from_baseline",
)


def _number(value: object) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid numeric mobility value: {value!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"mobility value must be finite: {value!r}")
    return number


def preprocess_data(records: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    prepared: list[dict[str, object]] = []
    seen_dates: set[str] = set()
    for index, record in enumerate(records, start=1):
        raw_date = str(record.get("date", "")).strip()
        try:
            parsed_date = datetime.strptime(raw_date, "%m-%d-%Y").date()
        except ValueError as exc:
            raise ValueError(f"row {index} has invalid date {raw_date!r}; expected MM-DD-YYYY") from exc
        iso_date = parsed_date.isoformat()
        if iso_date in seen_dates:
            raise ValueError(f"row {index} duplicates mobility date {iso_date}")
        seen_dates.add(iso_date)
        prepared_record: dict[str, object] = {"date": iso_date}
        for field in MOBILITY_FIELDS:
            prepared_record[field] = _number(record.get(field))
        prepared.append(prepared_record)
    prepared.sort(key=lambda item: str(item["date"]))
    return prepared
