from __future__ import annotations

import math
from datetime import date, datetime


def _day_of_year(date_text: str) -> int:
    try:
        parsed = datetime.strptime(str(date_text), "%Y-%m-%d").date()
    except ValueError:
        parsed = date(2026, 12, 21)
    return int(parsed.strftime("%j"))


def sun_position(latitude_deg: float, day_of_year: int, hour: float) -> dict:
    """Approximate solar altitude, azimuth, and vector.

    Coordinates follow the project convention: x=east, y=north, z=up.
    Azimuth is degrees clockwise from north.
    """
    lat = math.radians(latitude_deg)
    decl = math.radians(23.45) * math.sin(math.radians(360 * (284 + day_of_year) / 365))
    hour_angle = math.radians(15 * (hour - 12.0))

    sin_alt = math.sin(lat) * math.sin(decl) + math.cos(lat) * math.cos(decl) * math.cos(hour_angle)
    altitude = math.asin(max(-1.0, min(1.0, sin_alt)))

    azimuth_rad = math.atan2(
        math.sin(hour_angle),
        math.cos(hour_angle) * math.sin(lat) - math.tan(decl) * math.cos(lat),
    )
    azimuth_deg = (math.degrees(azimuth_rad) + 180.0) % 360.0

    vector = (
        math.cos(altitude) * math.sin(math.radians(azimuth_deg)),
        math.cos(altitude) * math.cos(math.radians(azimuth_deg)),
        math.sin(altitude),
    )
    return {
        "hour": hour,
        "altitude_deg": math.degrees(altitude),
        "azimuth_deg": azimuth_deg,
        "vector_x": vector[0],
        "vector_y": vector[1],
        "vector_z": vector[2],
    }


def sample_sun_path(site_config: dict, solar_config: dict) -> list[dict]:
    """Sample the configured winter-solstice solar path."""
    latitude = float(site_config.get("latitude", 24.55))
    day = _day_of_year(str(solar_config.get("winter_solstice_date", "2026-12-21")))
    start_hour = float(solar_config.get("start_hour", 8))
    end_hour = float(solar_config.get("end_hour", 16))
    step = float(solar_config.get("time_step_hours", 1.0))
    min_alt = float(solar_config.get("min_sun_altitude_deg", 1.0))

    samples: list[dict] = []
    hour = start_hour
    while hour <= end_hour + 1e-9:
        sample = sun_position(latitude, day, hour)
        sample["weight_hours"] = step
        sample["is_active"] = sample["altitude_deg"] >= min_alt
        samples.append(sample)
        hour += step
    return samples

