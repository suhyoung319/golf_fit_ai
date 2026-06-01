"""
Golf Fit AI API integration tests using the configured MySQL database.

Prerequisites:
  1. MySQL server is running
  2. DATABASE_URL is set in .env
  3. Seed data is loaded with: python seed_data.py

Run:
  python test_api.py
"""
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(__file__) or ".")

from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()

import app.models  # noqa: F401 - register all SQLAlchemy models on Base.metadata
from app.db.database import SessionLocal
from app.main import app
from app.models.club import Club, ClubCategory


client = TestClient(app)
results: list[bool] = []


NORMAL_CASES: list[tuple[str, str, dict[str, Any]]] = [
    (
        "driver 정상 추천",
        "driver",
        {
            "club_type": "driver",
            "handicap": 28,
            "driver_distance": 170,
            "miss_shot": "slice",
            "swing_speed": "slow",
        },
    ),
    (
        "wood 정상 추천",
        "wood",
        {
            "club_type": "wood",
            "handicap": 20,
            "wood_distance": 200,
            "fairway_miss": "thin",
            "trajectory": "high",
        },
    ),
    (
        "utility 정상 추천",
        "utility",
        {
            "club_type": "utility",
            "handicap": 25,
            "utility_distance": 180,
            "long_iron_difficulty": "hard",
            "trajectory": "high",
        },
    ),
    (
        "iron 정상 추천",
        "iron",
        {
            "club_type": "iron",
            "handicap": 18,
            "iron_7_distance": 135,
            "miss_shot": "duff",
            "trajectory": "mid",
        },
    ),
    (
        "wedge 정상 추천",
        "wedge",
        {
            "club_type": "wedge",
            "handicap": 12,
            "approach_distance": 80,
            "wedge_miss": "chunk",
            "spin_need": "high",
        },
    ),
    (
        "putter 정상 추천",
        "putter",
        {
            "club_type": "putter",
            "handicap": 8,
            "putting_miss": "left",
            "distance_control": "average",
            "stroke_type": "arc",
        },
    ),
]


VALIDATION_CASES: list[tuple[str, str, dict[str, Any]]] = [
    (
        "handicap 누락",
        "driver",
        {
            "club_type": "driver",
            "driver_distance": 170,
            "miss_shot": "slice",
            "swing_speed": "slow",
        },
    ),
    (
        "driver 필수 필드 driver_distance 누락",
        "driver",
        {
            "club_type": "driver",
            "handicap": 28,
            "miss_shot": "slice",
            "swing_speed": "slow",
        },
    ),
    (
        "wood 필수 필드 wood_distance 누락",
        "wood",
        {
            "club_type": "wood",
            "handicap": 20,
            "fairway_miss": "thin",
            "trajectory": "high",
        },
    ),
    (
        "utility 필수 필드 utility_distance 누락",
        "utility",
        {
            "club_type": "utility",
            "handicap": 25,
            "long_iron_difficulty": "hard",
            "trajectory": "high",
        },
    ),
    (
        "iron 필수 필드 iron_7_distance 누락",
        "iron",
        {
            "club_type": "iron",
            "handicap": 18,
            "miss_shot": "duff",
            "trajectory": "mid",
        },
    ),
    (
        "wedge 필수 필드 approach_distance 누락",
        "wedge",
        {
            "club_type": "wedge",
            "handicap": 12,
            "wedge_miss": "chunk",
            "spin_need": "high",
        },
    ),
    (
        "putter 필수 필드 handicap 누락",
        "putter",
        {
            "club_type": "putter",
            "putting_miss": "left",
            "distance_control": "average",
            "stroke_type": "arc",
        },
    ),
    (
        "잘못된 enum 값",
        "driver",
        {
            "club_type": "driver",
            "handicap": 28,
            "driver_distance": 170,
            "miss_shot": "banana",
            "swing_speed": "slow",
        },
    ),
]


def endpoint(club_type: str) -> str:
    return f"/api/recommend/{club_type}"


def print_validation_detail(resp) -> None:
    detail = resp.json().get("detail", "")
    if isinstance(detail, list):
        messages = []
        for item in detail:
            loc = ".".join(str(part) for part in item.get("loc", []))
            msg = item.get("msg", "")
            messages.append(f"{loc}: {msg}" if loc else msg)
        detail = " / ".join(messages)
    print(f"      HTTP {resp.status_code}  {str(detail)[:180]}")


def validate_top3_response(body: dict[str, Any], expected_club_type: str) -> list[str]:
    errors: list[str] = []

    if body.get("club_type") != expected_club_type:
        errors.append(f"club_type 불일치: {body.get('club_type')}")
    if "handicap" not in body:
        errors.append("handicap 누락")
    if "calculated_skill" not in body:
        errors.append("calculated_skill 누락")
    if "rule_top1" not in body:
        errors.append("rule_top1 누락")
    if "ml_agreement" not in body:
        errors.append("ml_agreement 키 누락")
    if "ml_prediction" not in body:
        errors.append("ml_prediction 키 누락")
    elif body["ml_prediction"] is not None:
        ml_prediction = body["ml_prediction"]
        if not isinstance(ml_prediction, dict):
            errors.append("ml_prediction 객체 아님")
        else:
            if not ml_prediction.get("category_name"):
                errors.append("ml_prediction.category_name 누락")
            confidence = ml_prediction.get("confidence")
            if confidence is None:
                errors.append("ml_prediction.confidence 누락")
            elif not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                errors.append(f"ml_prediction.confidence 범위 오류: {confidence}")
    elif body.get("ml_agreement") is not None:
        errors.append("ml_prediction이 null이면 ml_agreement도 null이어야 함")

    recommendations = body.get("recommendations")
    if not isinstance(recommendations, list):
        return errors + ["recommendations 배열 누락"]
    if len(recommendations) != 3:
        errors.append(f"recommendations 길이 {len(recommendations)} != 3")
    elif body.get("rule_top1") != recommendations[0].get("category_name"):
        errors.append(
            "rule_top1 불일치: "
            f"{body.get('rule_top1')} != {recommendations[0].get('category_name')}"
        )

    ml_prediction = body.get("ml_prediction")
    if isinstance(ml_prediction, dict):
        expected_agreement = ml_prediction.get("category_name") == body.get("rule_top1")
        if body.get("ml_agreement") != expected_agreement:
            errors.append(
                "ml_agreement 불일치: "
                f"{body.get('ml_agreement')} != {expected_agreement}"
            )

    for index, item in enumerate(recommendations, start=1):
        prefix = f"recommendations[{index}]"
        if item.get("rank") != index:
            errors.append(f"{prefix}.rank 불일치")
        if not item.get("category_name"):
            errors.append(f"{prefix}.category_name 누락")
        if "score" not in item:
            errors.append(f"{prefix}.score 누락")
        if not item.get("reason"):
            errors.append(f"{prefix}.reason 누락")
        if "matched_traits" not in item:
            errors.append(f"{prefix}.matched_traits 누락")
        elif not isinstance(item["matched_traits"], list):
            errors.append(f"{prefix}.matched_traits 배열 아님")
        clubs = item.get("clubs")
        if not isinstance(clubs, list):
            errors.append(f"{prefix}.clubs 배열 누락")
            continue
        if len(clubs) > 3:
            errors.append(f"{prefix}.clubs 길이 {len(clubs)} > 3")
        if len(clubs) == 0:
            errors.append(f"{prefix}.clubs 비어 있음")

        for club_index, club in enumerate(clubs, start=1):
            club_prefix = f"{prefix}.clubs[{club_index}]"
            required_fields = [
                "brand",
                "model_name",
                "club_type",
                "price_range",
            ]
            for field in required_fields:
                if not club.get(field):
                    errors.append(f"{club_prefix}.{field} 누락")
            if club.get("club_type") != expected_club_type:
                errors.append(f"{club_prefix}.club_type 불일치: {club.get('club_type')}")
            for score_field in [
                "forgiveness_score",
                "distance_score",
                "control_score",
                "spin_score",
            ]:
                score = club.get(score_field)
                if not isinstance(score, int) or score < 0 or score > 100:
                    errors.append(f"{club_prefix}.{score_field} 범위 오류: {score}")

    return errors


def print_recommendations(body: dict[str, Any]) -> None:
    for item in body.get("recommendations", []):
        print(
            f"      {item.get('rank')}위 | "
            f"{item.get('category_name')} | "
            f"score={item.get('score')}"
        )
        print(f"          reason={item.get('reason')}")
        print(f"          matched_traits={item.get('matched_traits', [])}")
        clubs = item.get("clubs", [])
        if clubs:
            print("          추천 클럽:")
            for club in clubs:
                print(
                    f"          - {club.get('brand')} {club.get('model_name')} / "
                    f"{club.get('price_range')} / "
                    f"forgiveness={club.get('forgiveness_score')}"
                )
        else:
            print("          추천 클럽: []")


def run_success_case(label: str, club_type: str, payload: dict[str, Any]) -> None:
    resp = client.post(endpoint(club_type), json=payload)
    ok = resp.status_code == 200
    body: dict[str, Any] = {}
    errors: list[str] = []

    if ok:
        body = resp.json()
        errors = validate_top3_response(body, club_type)
        ok = not errors

    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label}")

    if resp.status_code != 200:
        print_validation_detail(resp)
    elif errors:
        for error in errors:
            print(f"      검증 실패: {error}")
        print(f"      response={body}")
    else:
        print_recommendations(body)
    print()


def run_validation_case(label: str, club_type: str, payload: dict[str, Any]) -> None:
    resp = client.post(endpoint(club_type), json=payload)
    ok = resp.status_code == 422
    results.append(ok)

    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    print_validation_detail(resp)
    print()


def run_price_cases() -> None:
    db = SessionLocal()
    try:
        club = db.query(Club).order_by(Club.id.asc()).first()
    finally:
        db.close()

    if not club:
        results.append(False)
        print("FAIL  클럽 가격 목록 조회")
        print("      테스트할 클럽 데이터가 없습니다.")
        print()
        return

    resp = client.get(f"/api/clubs/{club.id}/prices")
    ok = resp.status_code == 200
    prices = resp.json() if ok else []
    if ok:
        price_values = [item.get("price") for item in prices]
        ok = (
            len(prices) >= 2
            and price_values == sorted(price_values)
            and all(item.get("club_id") == club.id for item in prices)
        )
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  클럽 가격 목록 조회")
    if not ok:
        print(f"      HTTP {resp.status_code} response={prices}")
    print()

    missing_resp = client.get("/api/clubs/999999999/prices")
    missing_ok = missing_resp.status_code == 404
    results.append(missing_ok)
    print(f"{'PASS' if missing_ok else 'FAIL'}  존재하지 않는 클럽 가격 404")
    if not missing_ok:
        print_validation_detail(missing_resp)
    print()


def check_db_connection() -> None:
    """Check MySQL connectivity and required seed data."""
    db = None
    try:
        db = SessionLocal()
        cat_count = db.query(ClubCategory).count()
        club_count = db.query(Club).count()
        print(f"  DB 연결 성공 - 카테고리 {cat_count}개 / 클럽 {club_count}개")
        if cat_count == 0 or club_count == 0:
            print("  시드 데이터 없음. 먼저 'python seed_data.py'를 실행하세요.")
            sys.exit(1)
        print()
    except Exception as exc:
        print(f"  DB 연결 실패: {exc}")
        print("  .env 파일의 DATABASE_URL과 MySQL 서버 상태를 확인하세요.")
        sys.exit(1)
    finally:
        if db is not None:
            db.close()


def test_all() -> None:
    print("=" * 65)
    print("  Golf Fit AI - API 통합 테스트 (MySQL)")
    print("=" * 65)
    print()

    print("[ DB 연결 확인 ]")
    check_db_connection()

    print("[ club_type별 정상 케이스 ]\n")
    for label, club_type, payload in NORMAL_CASES:
        run_success_case(label, club_type, payload)

    print("[ 유효성 검사 실패 (HTTP 422 기대) ]\n")
    for label, club_type, payload in VALIDATION_CASES:
        run_validation_case(label, club_type, payload)

    print("[ 클럽 최저가 API ]\n")
    run_price_cases()

    passed = sum(results)
    total = len(results)
    print("=" * 65)
    print(f"  결과: {passed}/{total} 통과  {'전체 통과' if passed == total else f'{total - passed}건 실패'}")
    print("=" * 65)


if __name__ == "__main__":
    test_all()
