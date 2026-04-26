from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from validation import FEATURE_COLUMNS, HouseFeatures


@lru_cache(maxsize=1)
def load_model(model_path: str = "model.pkl"):
    return joblib.load(model_path)


def predict_house_price(features: HouseFeatures, model=None) -> float:
    active_model = model or load_model()
    frame = pd.DataFrame(
        [[features[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS,
    )
    return float(active_model.predict(frame)[0])
