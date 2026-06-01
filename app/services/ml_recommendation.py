from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any


MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "recommendation_model.joblib"


FEATURE_COLUMNS = [
    "club_type",
    "handicap",
    "calculated_skill",
    "distance",
    "miss_shot",
    "trajectory",
    "swing_speed",
    "fairway_miss",
    "long_iron_difficulty",
    "wedge_miss",
    "spin_need",
    "putting_miss",
    "distance_control",
    "stroke_type",
]


def calculated_skill(handicap: int) -> str:
    if handicap >= 25:
        return "beginner"
    if handicap >= 10:
        return "intermediate"
    return "advanced"


@lru_cache(maxsize=1)
def _load_model() -> Any | None:
    if not MODEL_PATH.exists():
        return None
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def profile_to_features(profile) -> dict[str, Any]:
    data = profile.model_dump()
    club_type = data.get("club_type")

    distance = None
    if club_type == "driver":
        distance = data.get("driver_distance")
    elif club_type == "wood":
        distance = data.get("wood_distance")
    elif club_type == "utility":
        distance = data.get("utility_distance")
    elif club_type == "iron":
        distance = data.get("iron_7_distance")
    elif club_type == "wedge":
        distance = data.get("approach_distance")

    row = {
        "club_type": club_type,
        "handicap": data.get("handicap"),
        "calculated_skill": calculated_skill(data.get("handicap", 0)),
        "distance": distance,
        "miss_shot": data.get("miss_shot"),
        "trajectory": data.get("trajectory"),
        "swing_speed": data.get("swing_speed"),
        "fairway_miss": data.get("fairway_miss"),
        "long_iron_difficulty": data.get("long_iron_difficulty"),
        "wedge_miss": data.get("wedge_miss"),
        "spin_need": data.get("spin_need"),
        "putting_miss": data.get("putting_miss"),
        "distance_control": data.get("distance_control"),
        "stroke_type": data.get("stroke_type"),
    }
    return {column: row.get(column) for column in FEATURE_COLUMNS}


def predict_category(profile) -> dict[str, Any] | None:
    model = _load_model()
    if model is None:
        return None

    try:
        import pandas as pd

        features = pd.DataFrame([profile_to_features(profile)], columns=FEATURE_COLUMNS)
        predicted_category = model.predict(features)[0]
        confidence = None

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features)[0]
            confidence = round(float(max(probabilities)), 4)

        return {
            "category_name": str(predicted_category),
            "confidence": confidence,
        }
    except Exception:
        return None
