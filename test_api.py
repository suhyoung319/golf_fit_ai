"""
API 통합 테스트 — MySQL 연동 기준.

사전 조건:
  1. MySQL 서버 실행 중
  2. .env 파일에 DATABASE_URL 설정 완료
  3. python seed_data.py 실행 완료

실행:
  python test_api.py
"""
import sys, os
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

# ── MySQL 엔진으로 앱 그대로 사용 ─────────────────────────────
from app.db.database import Base, engine, get_db, SessionLocal
import app.models  # 모든 모델 Base.metadata 등록

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)  # 실제 MySQL get_db 그대로 사용

# ── 테스트 러너 ───────────────────────────────────────────────
results = []

def run(label, payload, expect_category=None, expect_status=200, expect_clubs_gte=0):
    resp = client.post("/api/recommend", json=payload)
    ok = (resp.status_code == expect_status)
    body = {}

    if ok and expect_status == 200:
        body = resp.json()
        if expect_category:
            ok = ok and (body.get("category_name") == expect_category)
        if expect_clubs_gte:
            ok = ok and (len(body.get("clubs", [])) >= expect_clubs_gte)

    tag = "✅ PASS" if ok else "❌ FAIL"
    results.append(ok)
    print(f"{tag}  {label}")

    if expect_status == 200 and body:
        print(f"      카테고리 : {body.get('category_name')}")
        print(f"      추천 이유 : {body.get('reason')}")
        for c in body.get("clubs", []):
            print(f"        · {c['brand']} {c['model_name']}  "
                  f"샤프트={c.get('shaft_type')}  {c.get('price_range')}")
    elif expect_status != 200:
        detail = resp.json().get("detail", "")
        if isinstance(detail, list):
            detail = " / ".join(d.get("msg", "") for d in detail)
        print(f"      HTTP {resp.status_code}  {str(detail)[:100]}")
    print()


def check_db_connection():
    """MySQL 연결 및 시드 데이터 확인."""
    try:
        db = SessionLocal()
        from app.models.club import ClubCategory, Club
        cat_count  = db.query(ClubCategory).count()
        club_count = db.query(Club).count()
        db.close()
        print(f"  DB 연결 성공 — 카테고리 {cat_count}개 / 클럽 {club_count}개")
        if cat_count == 0:
            print("  ⚠️  시드 데이터 없음. 먼저 'python seed_data.py'를 실행하세요.")
            sys.exit(1)
        print()
        return True
    except Exception as e:
        print(f"  ❌ DB 연결 실패: {e}")
        print("  .env 파일의 DATABASE_URL과 MySQL 서버 상태를 확인하세요.")
        sys.exit(1)


def test_all():
    print("=" * 65)
    print("  Golf Fit AI — API 통합 테스트 (MySQL)")
    print("=" * 65)
    print()
    print("[ DB 연결 확인 ]")
    check_db_connection()

    # ── 정상 케이스 ───────────────────────────────────────────
    print("[ 정상 케이스 ]\n")

    run("입문자 + 슬라이스 + slow → 고반발 드라이버",
        {"skill_level": "beginner", "miss_shot_type": "slice",
         "distance_avg": 150, "handicap": 36, "swing_speed": "slow"},
        expect_category="고반발 드라이버", expect_clubs_gte=2)

    run("입문자 + 탑핑 + slow → 페어웨이 우드",
        {"skill_level": "beginner", "miss_shot_type": "top",
         "distance_avg": 130, "handicap": 40, "swing_speed": "slow"},
        expect_category="페어웨이 우드")

    run("입문자 + 뒤땅 + slow → 하이브리드",
        {"skill_level": "beginner", "miss_shot_type": "fat",
         "distance_avg": 120, "handicap": 42, "swing_speed": "slow"},
        expect_category="하이브리드", expect_clubs_gte=1)

    run("아마추어 + 슬라이스 + medium → 드라이버",
        {"skill_level": "amateur", "miss_shot_type": "slice",
         "distance_avg": 180, "handicap": 24, "swing_speed": "medium"},
        expect_category="드라이버", expect_clubs_gte=2)

    run("아마추어 + 없음 + medium → 아이언 세트",
        {"skill_level": "amateur", "miss_shot_type": "none",
         "distance_avg": 190, "handicap": 20, "swing_speed": "medium"},
        expect_category="아이언 세트", expect_clubs_gte=1)

    run("중급자 + 뒤땅 + medium → 웨지",
        {"skill_level": "intermediate", "miss_shot_type": "fat",
         "distance_avg": 220, "handicap": 14, "swing_speed": "medium"},
        expect_category="웨지", expect_clubs_gte=2)

    run("상급자 + 없음 + fast → 포지드 아이언",
        {"skill_level": "advanced", "miss_shot_type": "none",
         "distance_avg": 290, "handicap": 3, "swing_speed": "fast"},
        expect_category="포지드 아이언", expect_clubs_gte=2)

    run("상급자 + 풀 + fast → 퍼터",
        {"skill_level": "advanced", "miss_shot_type": "pull",
         "distance_avg": 280, "handicap": 5, "swing_speed": "fast"},
        expect_category="퍼터", expect_clubs_gte=1)

    run("핸디캡 null 허용",
        {"skill_level": "amateur", "miss_shot_type": "hook",
         "distance_avg": 170, "swing_speed": "medium"},
        expect_category="드라이버")

    # ── 엣지 케이스 ───────────────────────────────────────────
    print("[ 엣지 케이스 ]\n")

    run("비거리 최솟값 50야드",
        {"skill_level": "beginner", "miss_shot_type": "none",
         "distance_avg": 50, "swing_speed": "slow"},
        expect_category="고반발 드라이버")

    run("비거리 최댓값 400야드",
        {"skill_level": "advanced", "miss_shot_type": "none",
         "distance_avg": 400, "swing_speed": "fast"},
        expect_category="포지드 아이언")

    run("핸디캡 0 허용",
        {"skill_level": "advanced", "miss_shot_type": "none",
         "distance_avg": 300, "handicap": 0, "swing_speed": "fast"},
        expect_category="포지드 아이언")

    # ── 유효성 검사 실패 (422) ────────────────────────────────
    print("[ 유효성 검사 실패 (HTTP 422 기대) ]\n")

    run("비거리 500야드 초과",
        {"skill_level": "beginner", "miss_shot_type": "none",
         "distance_avg": 500, "swing_speed": "slow"},
        expect_status=422)

    run("비거리 음수",
        {"skill_level": "amateur", "miss_shot_type": "none",
         "distance_avg": -1, "swing_speed": "medium"},
        expect_status=422)

    run("핸디캡 55 초과",
        {"skill_level": "beginner", "miss_shot_type": "none",
         "distance_avg": 150, "handicap": 55, "swing_speed": "slow"},
        expect_status=422)

    run("잘못된 skill_level 값 'pro'",
        {"skill_level": "pro", "miss_shot_type": "none",
         "distance_avg": 200, "swing_speed": "medium"},
        expect_status=422)

    run("필수 필드 distance_avg 누락",
        {"skill_level": "amateur", "miss_shot_type": "none",
         "swing_speed": "medium"},
        expect_status=422)

    # ── 결과 요약 ─────────────────────────────────────────────
    passed = sum(results)
    total  = len(results)
    print("=" * 65)
    print(f"  결과: {passed}/{total} 통과  "
          f"{'✅ 전체 통과' if passed == total else f'❌ {total - passed}건 실패'}")
    print("=" * 65)


if __name__ == "__main__":
    test_all()
