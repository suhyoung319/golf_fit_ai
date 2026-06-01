from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.services.ml_recommendation import FEATURE_COLUMNS


DATA_PATH = PROJECT_ROOT / "data" / "training_data.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "recommendation_model.joblib"
TARGET_COLUMN = "label"


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run: python scripts/generate_training_data.py"
        )

    df = pd.read_csv(DATA_PATH)
    missing_columns = [column for column in FEATURE_COLUMNS + [TARGET_COLUMN] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in training data: {missing_columns}")

    x = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    numeric_features = ["handicap", "distance"]
    categorical_features = [column for column in FEATURE_COLUMNS if column not in numeric_features]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                SimpleImputer(strategy="median"),
                numeric_features,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value="none")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print()
    print(classification_report(y_test, predictions))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
