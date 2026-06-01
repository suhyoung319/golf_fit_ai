from __future__ import annotations

import csv
import random
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import SessionLocal
from app.schemas.user_input import (
    DriverInput,
    IronInput,
    PutterInput,
    UtilityInput,
    WedgeInput,
    WoodInput,
)
from app.services.ml_recommendation import FEATURE_COLUMNS, calculated_skill
from app.services.recommendation import recommend_clubs


OUTPUT_PATH = PROJECT_ROOT / "data" / "training_data.csv"
ROWS_PER_CLUB_TYPE = 600
RANDOM_SEED = 42

CSV_COLUMNS = FEATURE_COLUMNS + ["label"]


def _none_row(club_type: str, handicap: int) -> dict[str, Any]:
    return {
        "club_type": club_type,
        "handicap": handicap,
        "calculated_skill": calculated_skill(handicap),
        "distance": None,
        "miss_shot": "none",
        "trajectory": "none",
        "swing_speed": "none",
        "fairway_miss": "none",
        "long_iron_difficulty": "none",
        "wedge_miss": "none",
        "spin_need": "none",
        "putting_miss": "none",
        "distance_control": "none",
        "stroke_type": "none",
    }


def make_profile(club_type: str):
    handicap = random.randint(0, 54)

    if club_type == "driver":
        return DriverInput(
            club_type="driver",
            handicap=handicap,
            driver_distance=random.randint(130, 290),
            miss_shot=random.choice(["slice", "hook", "high", "low", "none"]),
            swing_speed=random.choice(["slow", "medium", "fast"]),
        )
    if club_type == "wood":
        return WoodInput(
            club_type="wood",
            handicap=handicap,
            wood_distance=random.randint(120, 260),
            fairway_miss=random.choice(["thin", "fat", "left", "right", "none"]),
            trajectory=random.choice(["low", "mid", "high"]),
        )
    if club_type == "utility":
        return UtilityInput(
            club_type="utility",
            handicap=handicap,
            utility_distance=random.randint(110, 240),
            long_iron_difficulty=random.choice(["very_hard", "hard", "ok"]),
            trajectory=random.choice(["low", "mid", "high"]),
        )
    if club_type == "iron":
        return IronInput(
            club_type="iron",
            handicap=handicap,
            iron_7_distance=random.randint(90, 190),
            miss_shot=random.choice(["top", "duff", "pull", "push", "none"]),
            trajectory=random.choice(["low", "mid", "high"]),
        )
    if club_type == "wedge":
        return WedgeInput(
            club_type="wedge",
            handicap=handicap,
            approach_distance=random.randint(20, 130),
            wedge_miss=random.choice(["short", "long", "skull", "chunk", "none"]),
            spin_need=random.choice(["high", "medium", "low"]),
        )
    if club_type == "putter":
        return PutterInput(
            club_type="putter",
            handicap=handicap,
            putting_miss=random.choice(["short", "long", "left", "right", "none"]),
            distance_control=random.choice(["poor", "average", "good"]),
            stroke_type=random.choice(["straight", "arc"]),
        )
    raise ValueError(f"Unsupported club_type: {club_type}")


def profile_to_row(profile, label: str) -> dict[str, Any]:
    data = profile.model_dump()
    row = _none_row(data["club_type"], data["handicap"])

    if data["club_type"] == "driver":
        row["distance"] = data["driver_distance"]
        row["miss_shot"] = data["miss_shot"]
        row["swing_speed"] = data["swing_speed"]
    elif data["club_type"] == "wood":
        row["distance"] = data["wood_distance"]
        row["fairway_miss"] = data["fairway_miss"]
        row["trajectory"] = data["trajectory"]
    elif data["club_type"] == "utility":
        row["distance"] = data["utility_distance"]
        row["long_iron_difficulty"] = data["long_iron_difficulty"]
        row["trajectory"] = data["trajectory"]
    elif data["club_type"] == "iron":
        row["distance"] = data["iron_7_distance"]
        row["miss_shot"] = data["miss_shot"]
        row["trajectory"] = data["trajectory"]
    elif data["club_type"] == "wedge":
        row["distance"] = data["approach_distance"]
        row["wedge_miss"] = data["wedge_miss"]
        row["spin_need"] = data["spin_need"]
    elif data["club_type"] == "putter":
        row["putting_miss"] = data["putting_miss"]
        row["distance_control"] = data["distance_control"]
        row["stroke_type"] = data["stroke_type"]

    row["label"] = label
    return row


def main() -> None:
    random.seed(RANDOM_SEED)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    db = SessionLocal()
    try:
        for club_type in ["driver", "wood", "utility", "iron", "wedge", "putter"]:
            for _ in range(ROWS_PER_CLUB_TYPE):
                profile = make_profile(club_type)
                response = recommend_clubs(profile, db)
                if not response.recommendations:
                    raise RuntimeError(f"No recommendation generated for {profile}")
                label = response.recommendations[0].category_name
                rows.append(profile_to_row(profile, label))
    finally:
        db.close()

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
