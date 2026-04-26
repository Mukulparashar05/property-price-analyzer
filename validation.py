from __future__ import annotations

from typing import Any, TypedDict, cast


class HouseFeatures(TypedDict):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str


FEATURE_COLUMNS = [
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
    "ocean_proximity",
]

VALID_OCEAN_PROXIMITIES = [
    "INLAND",
    "NEAR BAY",
    "NEAR OCEAN",
    "ISLAND",
    "<1H OCEAN",
]

DEFAULT_FEATURES: HouseFeatures = {
    "longitude": -118.49,
    "latitude": 34.26,
    "housing_median_age": 29.0,
    "total_rooms": 2127.0,
    "total_bedrooms": 435.0,
    "population": 1166.0,
    "households": 409.0,
    "median_income": 3.5348,
    "ocean_proximity": "INLAND",
}


def build_feature_payload(
    longitude: float,
    latitude: float,
    housing_median_age: float,
    total_rooms: float,
    total_bedrooms: float,
    population: float,
    households: float,
    median_income: float,
    ocean_proximity: str,
) -> HouseFeatures:
    return {
        "longitude": float(longitude),
        "latitude": float(latitude),
        "housing_median_age": float(housing_median_age),
        "total_rooms": float(total_rooms),
        "total_bedrooms": float(total_bedrooms),
        "population": float(population),
        "households": float(households),
        "median_income": float(median_income),
        "ocean_proximity": str(ocean_proximity),
    }


def validate_manual_features(features: HouseFeatures) -> list[str]:
    errors: list[str] = []

    if not (-125 <= features["longitude"] <= -113):
        errors.append("Longitude should be between -125 and -113")
    if not (32 <= features["latitude"] <= 42):
        errors.append("Latitude should be between 32 and 42")
    if features["total_rooms"] <= 0:
        errors.append("Total rooms must be greater than 0")
    if features["total_bedrooms"] < 0:
        errors.append("Total bedrooms cannot be negative")
    if features["total_bedrooms"] > features["total_rooms"]:
        errors.append("Bedrooms cannot be greater than total rooms")
    if features["population"] <= 0:
        errors.append("Population must be greater than 0")
    if features["households"] <= 0:
        errors.append("Households must be greater than 0")
    if features["households"] > features["population"]:
        errors.append("Households cannot exceed population")
    if not (0 < features["median_income"] <= 20):
        errors.append("Median income should be between 0 and 20")
    if features["ocean_proximity"] not in VALID_OCEAN_PROXIMITIES:
        errors.append("Invalid ocean proximity value")

    return errors


def _to_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def normalize_chat_features(candidate: dict[str, Any]) -> HouseFeatures:
    result: dict[str, Any] = dict(DEFAULT_FEATURES)

    result["longitude"] = min(
        max(_to_float(candidate.get("longitude"), DEFAULT_FEATURES["longitude"]), -125.0),
        -113.0,
    )
    result["latitude"] = min(
        max(_to_float(candidate.get("latitude"), DEFAULT_FEATURES["latitude"]), 32.0),
        42.0,
    )

    housing_median_age = _to_float(
        candidate.get("housing_median_age"),
        DEFAULT_FEATURES["housing_median_age"],
    )
    result["housing_median_age"] = (
        housing_median_age
        if housing_median_age >= 0
        else DEFAULT_FEATURES["housing_median_age"]
    )

    total_rooms = _to_float(candidate.get("total_rooms"), DEFAULT_FEATURES["total_rooms"])
    if total_rooms <= 0:
        total_rooms = DEFAULT_FEATURES["total_rooms"]
    result["total_rooms"] = total_rooms

    total_bedrooms = _to_float(
        candidate.get("total_bedrooms"),
        DEFAULT_FEATURES["total_bedrooms"],
    )
    if total_bedrooms < 0:
        total_bedrooms = DEFAULT_FEATURES["total_bedrooms"]
    result["total_bedrooms"] = min(total_bedrooms, result["total_rooms"])

    population = _to_float(candidate.get("population"), DEFAULT_FEATURES["population"])
    if population <= 0:
        population = DEFAULT_FEATURES["population"]
    result["population"] = population

    households = _to_float(candidate.get("households"), DEFAULT_FEATURES["households"])
    if households <= 0:
        households = DEFAULT_FEATURES["households"]
    result["households"] = min(households, result["population"])

    median_income = _to_float(
        candidate.get("median_income"),
        DEFAULT_FEATURES["median_income"],
    )
    if not (0 < median_income <= 20):
        median_income = DEFAULT_FEATURES["median_income"]
    result["median_income"] = median_income

    ocean_proximity = str(
        candidate.get("ocean_proximity", DEFAULT_FEATURES["ocean_proximity"])
    ).upper()
    if ocean_proximity not in VALID_OCEAN_PROXIMITIES:
        ocean_proximity = DEFAULT_FEATURES["ocean_proximity"]
    result["ocean_proximity"] = ocean_proximity

    return cast(HouseFeatures, result)
