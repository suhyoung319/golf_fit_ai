"""
club_type별 Top3 추천 함수.

흐름:
  1. handicap → skill 자동 계산
  2. club_type별 후보 카테고리 목록 정의
  3. 각 카테고리에 scorer.py로 점수 산출
  4. 점수 내림차순 정렬 → Top3 슬라이싱
  5. 각 카테고리 DB 조회 → 클럽 리스트 첨부
  6. reason_builder로 개별 이유 생성
  7. Top3Response 반환

ML 확장 포인트:
  - 학습 데이터: (입력 프로필, matched_traits, score, 카테고리) 로그가 자연스러운 피처/레이블
  - scorer.py의 calc_score()만 ML 모델 추론으로 교체하면 나머지 구조는 그대로 유지
"""
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.models.club import Club, ClubCategory
from app.schemas.user_input import (
    DriverInput, WoodInput, UtilityInput,
    IronInput, WedgeInput, PutterInput,
    ClubResponse, RecommendationItem, Top3Response,
)
from app.services.scorer import calc_score
from app.services.reason_builder import build_reason
from app.services.ml_recommendation import predict_category


# ── 공통 유틸 ─────────────────────────────────────────────────────

def _calc_skill(handicap: int) -> str:
    if handicap >= 25: return "beginner"
    if handicap >= 10: return "intermediate"
    return "advanced"

def _fetch_clubs(
    db: Session,
    category: ClubCategory,
    profile,
    limit: int = 3,
) -> list[ClubResponse]:
    if profile.club_type == "wedge":
        order_by = [desc(Club.spin_score), desc(Club.control_score)]
    elif profile.club_type == "putter":
        order_by = [desc(Club.control_score), desc(Club.forgiveness_score)]
    else:
        order_by = [
            desc(Club.forgiveness_score),
            desc(Club.distance_score),
            desc(Club.control_score),
        ]

    clubs = (
        db.query(Club)
        .filter(
            Club.category_id == category.id,
            Club.club_type == profile.club_type,
        )
        .order_by(*order_by)
        .limit(limit)
        .all()
    )
    return [ClubResponse.model_validate(c) for c in clubs]


def _get_category(db: Session, name: str) -> ClubCategory | None:
    return db.query(ClubCategory).filter(ClubCategory.name == name).first()


def _build_top3(
    profile,
    db: Session,
    candidates: list[str],          # 이 club_type에서 가능한 카테고리명 목록
) -> Top3Response:
    """
    후보 카테고리 목록을 점수화 → Top3 선택 → 클럽 조회 → 응답 조립.
    DB에 없는 카테고리는 자동으로 건너뜀.
    """
    skill = _calc_skill(profile.handicap)

    # 점수 산출
    scored = []
    for cat_name in candidates:
        score, matched = calc_score(profile, cat_name)
        scored.append((cat_name, score, matched))

    # 점수 내림차순 정렬
    scored.sort(key=lambda x: x[1], reverse=True)

    # Top3 조립
    items: list[RecommendationItem] = []
    rank = 1
    for cat_name, score, matched in scored:
        if rank > 3:
            break
        category = _get_category(db, cat_name)
        if not category:
            continue  # DB 미등록 카테고리는 스킵

        clubs  = _fetch_clubs(db, category, profile)
        reason = build_reason(profile, cat_name, matched)

        items.append(RecommendationItem(
            rank=rank,
            category_name=cat_name,
            score=score,
            reason=reason,
            matched_traits=matched,
            clubs=clubs,
        ))
        rank += 1

    rule_top1 = items[0].category_name if items else None
    ml_prediction = predict_category(profile)
    ml_agreement = (
        None
        if ml_prediction is None
        else ml_prediction.get("category_name") == rule_top1
    )

    return Top3Response(
        club_type=profile.club_type,
        handicap=profile.handicap,
        calculated_skill=skill,
        rule_top1=rule_top1,
        ml_prediction=ml_prediction,
        ml_agreement=ml_agreement,
        recommendations=items,
    )


# ── 드라이버 ─────────────────────────────────────────────────────

_DRIVER_CANDIDATES = ["고반발 드라이버", "슬라이스 보정 드라이버", "드라이버", "투어 드라이버"]

def recommend_driver(profile: DriverInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _DRIVER_CANDIDATES)


# ── 페어웨이 우드 ─────────────────────────────────────────────────

_WOOD_CANDIDATES = ["페어웨이 우드", "로우스핀 우드", "고탄도 우드"]

def recommend_wood(profile: WoodInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _WOOD_CANDIDATES)


# ── 유틸리티 ─────────────────────────────────────────────────────

_UTILITY_CANDIDATES = ["하이브리드", "로우스핀 유틸", "고탄도 유틸"]

def recommend_utility(profile: UtilityInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _UTILITY_CANDIDATES)


# ── 아이언 ───────────────────────────────────────────────────────

_IRON_CANDIDATES = ["아이언 세트", "포지드 아이언", "게임 임프루브먼트 아이언"]

def recommend_iron(profile: IronInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _IRON_CANDIDATES)


# ── 웨지 ─────────────────────────────────────────────────────────

_WEDGE_CANDIDATES = ["웨지", "로브 웨지", "갭 웨지"]

def recommend_wedge(profile: WedgeInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _WEDGE_CANDIDATES)


# ── 퍼터 ─────────────────────────────────────────────────────────

_PUTTER_CANDIDATES = ["퍼터", "말렛 퍼터", "블레이드 퍼터"]

def recommend_putter(profile: PutterInput, db: Session) -> Top3Response:
    return _build_top3(profile, db, _PUTTER_CANDIDATES)


# ── 디스패처 ─────────────────────────────────────────────────────

def recommend_clubs(profile, db: Session) -> Top3Response:
    dispatch = {
        "driver":  recommend_driver,
        "wood":    recommend_wood,
        "utility": recommend_utility,
        "iron":    recommend_iron,
        "wedge":   recommend_wedge,
        "putter":  recommend_putter,
    }
    fn = dispatch.get(profile.club_type)
    if fn:
        return fn(profile, db)
    raise ValueError(f"알 수 없는 club_type: {profile.club_type}")
