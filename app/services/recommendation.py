from sqlalchemy.orm import Session
from app.models.user_golf_profile import MissShotType, SwingSpeed
from app.models.club import Club, ClubCategory, ClubType
from app.schemas.user_input import GolfProfileInput, RecommendationResponse
from app.services.reason_builder import build_reason


# ── handicap → 내부 skill_level 자동 계산 ────────────────────────
def _calc_skill(handicap: int) -> str:
    """
    handicap 값만으로 실력 등급 결정.
    프론트에서 skill_level 을 받지 않으므로 여기서만 계산됨.
    """
    if handicap >= 25:
        return "beginner"
    if handicap >= 10:
        return "intermediate"
    return "advanced"


# ── 룰 테이블: (skill, miss_shot, club_type) → 카테고리명 ─────────
# club_type 이 고정되므로 시스템이 다른 종류로 이탈하지 않음.
# 같은 club_type 안에서 skill + miss_shot 조합으로 세부 카테고리만 결정.
RULE_TABLE: dict[tuple, str] = {
    # ── driver ────────────────────────────────────────────────────
    ("beginner",     "slice",  "driver"): "고반발 드라이버",
    ("beginner",     "hook",   "driver"): "고반발 드라이버",
    ("beginner",     "top",    "driver"): "고반발 드라이버",
    ("beginner",     "fat",    "driver"): "고반발 드라이버",
    ("beginner",     "push",   "driver"): "고반발 드라이버",
    ("beginner",     "pull",   "driver"): "고반발 드라이버",
    ("beginner",     "none",   "driver"): "고반발 드라이버",
    ("intermediate", "slice",  "driver"): "드라이버",
    ("intermediate", "hook",   "driver"): "드라이버",
    ("intermediate", "none",   "driver"): "드라이버",
    ("intermediate", "push",   "driver"): "드라이버",
    ("intermediate", "pull",   "driver"): "드라이버",
    ("intermediate", "top",    "driver"): "드라이버",
    ("intermediate", "fat",    "driver"): "드라이버",
    ("advanced",     "none",   "driver"): "드라이버",
    ("advanced",     "slice",  "driver"): "드라이버",
    ("advanced",     "hook",   "driver"): "드라이버",
    ("advanced",     "push",   "driver"): "드라이버",
    ("advanced",     "pull",   "driver"): "드라이버",
    ("advanced",     "top",    "driver"): "드라이버",
    ("advanced",     "fat",    "driver"): "드라이버",

    # ── wood ──────────────────────────────────────────────────────
    ("beginner",     "none",   "wood"):   "페어웨이 우드",
    ("beginner",     "top",    "wood"):   "페어웨이 우드",
    ("beginner",     "fat",    "wood"):   "페어웨이 우드",
    ("beginner",     "slice",  "wood"):   "페어웨이 우드",
    ("beginner",     "hook",   "wood"):   "페어웨이 우드",
    ("beginner",     "push",   "wood"):   "페어웨이 우드",
    ("beginner",     "pull",   "wood"):   "페어웨이 우드",
    ("intermediate", "none",   "wood"):   "페어웨이 우드",
    ("intermediate", "slice",  "wood"):   "페어웨이 우드",
    ("intermediate", "hook",   "wood"):   "페어웨이 우드",
    ("intermediate", "top",    "wood"):   "페어웨이 우드",
    ("intermediate", "fat",    "wood"):   "페어웨이 우드",
    ("intermediate", "push",   "wood"):   "페어웨이 우드",
    ("intermediate", "pull",   "wood"):   "페어웨이 우드",
    ("advanced",     "none",   "wood"):   "페어웨이 우드",
    ("advanced",     "slice",  "wood"):   "페어웨이 우드",
    ("advanced",     "hook",   "wood"):   "페어웨이 우드",
    ("advanced",     "top",    "wood"):   "페어웨이 우드",
    ("advanced",     "fat",    "wood"):   "페어웨이 우드",
    ("advanced",     "push",   "wood"):   "페어웨이 우드",
    ("advanced",     "pull",   "wood"):   "페어웨이 우드",

    # ── utility ───────────────────────────────────────────────────
    ("beginner",     "none",   "utility"): "하이브리드",
    ("beginner",     "fat",    "utility"): "하이브리드",
    ("beginner",     "top",    "utility"): "하이브리드",
    ("beginner",     "slice",  "utility"): "하이브리드",
    ("beginner",     "hook",   "utility"): "하이브리드",
    ("beginner",     "push",   "utility"): "하이브리드",
    ("beginner",     "pull",   "utility"): "하이브리드",
    ("intermediate", "none",   "utility"): "하이브리드",
    ("intermediate", "fat",    "utility"): "하이브리드",
    ("intermediate", "top",    "utility"): "하이브리드",
    ("intermediate", "slice",  "utility"): "하이브리드",
    ("intermediate", "hook",   "utility"): "하이브리드",
    ("intermediate", "push",   "utility"): "하이브리드",
    ("intermediate", "pull",   "utility"): "하이브리드",
    ("advanced",     "none",   "utility"): "하이브리드",
    ("advanced",     "fat",    "utility"): "하이브리드",
    ("advanced",     "top",    "utility"): "하이브리드",
    ("advanced",     "slice",  "utility"): "하이브리드",
    ("advanced",     "hook",   "utility"): "하이브리드",
    ("advanced",     "push",   "utility"): "하이브리드",
    ("advanced",     "pull",   "utility"): "하이브리드",

    # ── iron ──────────────────────────────────────────────────────
    ("beginner",     "none",   "iron"):   "아이언 세트",
    ("beginner",     "slice",  "iron"):   "아이언 세트",
    ("beginner",     "hook",   "iron"):   "아이언 세트",
    ("beginner",     "top",    "iron"):   "아이언 세트",
    ("beginner",     "fat",    "iron"):   "아이언 세트",
    ("beginner",     "push",   "iron"):   "아이언 세트",
    ("beginner",     "pull",   "iron"):   "아이언 세트",
    ("intermediate", "none",   "iron"):   "아이언 세트",
    ("intermediate", "slice",  "iron"):   "아이언 세트",
    ("intermediate", "hook",   "iron"):   "아이언 세트",
    ("intermediate", "top",    "iron"):   "아이언 세트",
    ("intermediate", "fat",    "iron"):   "아이언 세트",
    ("intermediate", "push",   "iron"):   "아이언 세트",
    ("intermediate", "pull",   "iron"):   "아이언 세트",
    ("advanced",     "none",   "iron"):   "포지드 아이언",
    ("advanced",     "slice",  "iron"):   "포지드 아이언",
    ("advanced",     "hook",   "iron"):   "포지드 아이언",
    ("advanced",     "top",    "iron"):   "포지드 아이언",
    ("advanced",     "fat",    "iron"):   "포지드 아이언",
    ("advanced",     "push",   "iron"):   "포지드 아이언",
    ("advanced",     "pull",   "iron"):   "포지드 아이언",

    # ── wedge ─────────────────────────────────────────────────────
    ("beginner",     "none",   "wedge"):  "웨지",
    ("beginner",     "fat",    "wedge"):  "웨지",
    ("beginner",     "slice",  "wedge"):  "웨지",
    ("beginner",     "hook",   "wedge"):  "웨지",
    ("beginner",     "top",    "wedge"):  "웨지",
    ("beginner",     "push",   "wedge"):  "웨지",
    ("beginner",     "pull",   "wedge"):  "웨지",
    ("intermediate", "none",   "wedge"):  "웨지",
    ("intermediate", "fat",    "wedge"):  "웨지",
    ("intermediate", "slice",  "wedge"):  "웨지",
    ("intermediate", "hook",   "wedge"):  "웨지",
    ("intermediate", "top",    "wedge"):  "웨지",
    ("intermediate", "push",   "wedge"):  "웨지",
    ("intermediate", "pull",   "wedge"):  "웨지",
    ("advanced",     "none",   "wedge"):  "웨지",
    ("advanced",     "fat",    "wedge"):  "웨지",
    ("advanced",     "slice",  "wedge"):  "웨지",
    ("advanced",     "hook",   "wedge"):  "웨지",
    ("advanced",     "top",    "wedge"):  "웨지",
    ("advanced",     "push",   "wedge"):  "웨지",
    ("advanced",     "pull",   "wedge"):  "웨지",

    # ── putter ────────────────────────────────────────────────────
    ("beginner",     "none",   "putter"): "퍼터",
    ("beginner",     "pull",   "putter"): "퍼터",
    ("beginner",     "push",   "putter"): "퍼터",
    ("beginner",     "slice",  "putter"): "퍼터",
    ("beginner",     "hook",   "putter"): "퍼터",
    ("beginner",     "top",    "putter"): "퍼터",
    ("beginner",     "fat",    "putter"): "퍼터",
    ("intermediate", "none",   "putter"): "퍼터",
    ("intermediate", "pull",   "putter"): "퍼터",
    ("intermediate", "push",   "putter"): "퍼터",
    ("intermediate", "slice",  "putter"): "퍼터",
    ("intermediate", "hook",   "putter"): "퍼터",
    ("intermediate", "top",    "putter"): "퍼터",
    ("intermediate", "fat",    "putter"): "퍼터",
    ("advanced",     "none",   "putter"): "퍼터",
    ("advanced",     "pull",   "putter"): "퍼터",
    ("advanced",     "push",   "putter"): "퍼터",
    ("advanced",     "slice",  "putter"): "퍼터",
    ("advanced",     "hook",   "putter"): "퍼터",
    ("advanced",     "top",    "putter"): "퍼터",
    ("advanced",     "fat",    "putter"): "퍼터",
}

# club_type 별 기본 카테고리 (룰 미매칭 폴백)
DEFAULT_BY_TYPE: dict[str, str] = {
    "driver":  "드라이버",
    "wood":    "페어웨이 우드",
    "utility": "하이브리드",
    "iron":    "아이언 세트",
    "wedge":   "웨지",
    "putter":  "퍼터",
}

# 스윙 속도 → 선호 샤프트
SHAFT_MAP: dict[str, list[str]] = {
    "slow":   ["senior", "ladies", "regular"],
    "medium": ["regular", "stiff"],
    "fast":   ["stiff", "extra_stiff"],
}


def _get_category_name(skill: str, miss: str, club_type: str) -> str:
    """룰 테이블에서 카테고리명 결정. 미매칭 시 club_type 기본값 반환."""
    return RULE_TABLE.get(
        (skill, miss, club_type),
        DEFAULT_BY_TYPE.get(club_type, "드라이버")
    )


def recommend_clubs(
    profile: GolfProfileInput,
    db: Session,
) -> RecommendationResponse:
    """
    메인 추천 함수.
    1. handicap → skill 자동 계산
    2. (skill, miss_shot, club_type) → 카테고리명 결정
    3. DB에서 해당 카테고리 + 샤프트 필터로 클럽 조회
    4. 추천 이유 생성 후 반환
    """
    skill         = _calc_skill(profile.handicap)
    category_name = _get_category_name(skill, profile.miss_shot_type, profile.club_type)

    category = (
        db.query(ClubCategory)
        .filter(ClubCategory.name == category_name)
        .first()
    )

    if not category:
        return RecommendationResponse(
            club_type=profile.club_type,
            category_name=category_name,
            reason="해당 카테고리 데이터가 없습니다. seed_data.py를 먼저 실행하세요.",
            clubs=[],
        )

    preferred_shafts = SHAFT_MAP.get(profile.swing_speed, ["regular"])

    clubs = (
        db.query(Club)
        .filter(
            Club.category_id == category.id,
            Club.shaft_type.in_(preferred_shafts),
        )
        .limit(3)
        .all()
    )

    # 샤프트 필터 결과 없으면 카테고리 전체에서 재조회
    if not clubs:
        clubs = (
            db.query(Club)
            .filter(Club.category_id == category.id)
            .limit(3)
            .all()
        )

    reason = build_reason(profile, category_name)

    return RecommendationResponse(
        club_type=profile.club_type,
        category_name=category_name,
        reason=reason,
        clubs=clubs,
    )
