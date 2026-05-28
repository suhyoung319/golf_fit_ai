from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user_input import GolfProfileInput, RecommendationResponse
from app.services.recommendation import recommend_clubs

router = APIRouter()


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(
    profile: GolfProfileInput,
    db: Session = Depends(get_db),
):
    """
    골프 프로필 입력 → 클럽 추천 반환.

    - skill_level: beginner / amateur / intermediate / advanced
    - miss_shot_type: slice / hook / top / fat / push / pull / none
    - distance_avg: 드라이버 평균 비거리 (야드, 50~400)
    - handicap: 핸디캡 (0~54, 없으면 null)
    - swing_speed: slow / medium / fast
    """
    return recommend_clubs(profile, db)
