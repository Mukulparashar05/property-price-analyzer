from validation import (
    DEFAULT_FEATURES,
    build_feature_payload,
    normalize_chat_features,
    validate_manual_features,
)


def test_validate_manual_features_reports_invalid_values():
    payload = build_feature_payload(
        longitude=-130.0,
        latitude=10.0,
        housing_median_age=20.0,
        total_rooms=0.0,
        total_bedrooms=3.0,
        population=0.0,
        households=4.0,
        median_income=25.0,
        ocean_proximity="MARS",
    )

    assert validate_manual_features(payload) == [
        "Longitude should be between -125 and -113",
        "Latitude should be between 32 and 42",
        "Total rooms must be greater than 0",
        "Bedrooms cannot be greater than total rooms",
        "Population must be greater than 0",
        "Households cannot exceed population",
        "Median income should be between 0 and 20",
        "Invalid ocean proximity value",
    ]


def test_normalize_chat_features_fills_missing_and_repairs_invalid_values():
    result = normalize_chat_features(
        {
            "latitude": 55,
            "housing_median_age": -2,
            "total_rooms": 0,
            "total_bedrooms": 3000,
            "population": 100,
            "households": 500,
            "median_income": -3,
            "ocean_proximity": "near ocean",
        }
    )

    assert result == {
        "longitude": DEFAULT_FEATURES["longitude"],
        "latitude": 42.0,
        "housing_median_age": DEFAULT_FEATURES["housing_median_age"],
        "total_rooms": DEFAULT_FEATURES["total_rooms"],
        "total_bedrooms": DEFAULT_FEATURES["total_rooms"],
        "population": 100.0,
        "households": 100.0,
        "median_income": DEFAULT_FEATURES["median_income"],
        "ocean_proximity": "NEAR OCEAN",
    }
