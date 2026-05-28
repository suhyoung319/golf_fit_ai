from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.user_golf_profile import MissShotType, SwingSpeed
from app.models.club import ClubType


class GolfProfileInput(BaseModel):
    """
    추천 요청 입력값.
    - skill_level 제거 → handicap 으로 내부 자동 계산
    - club_type 추가   → 사용자가 원하는 클럽 종류 직접 선택
    """
    club_type:      ClubType
    miss_shot_type: MissShotType = MissShotType.none
    distance_avg:   int          = Field(..., ge=50, le=400, description="드라이버 평균 비거리 (야드)")
    handicap:       int          = Field(..., ge=0,  le=54,  description="핸디캡 (0~54)")
    swing_speed:    SwingSpeed   = SwingSpeed.medium

    model_config = {"use_enum_values": True}


class ClubResponse(BaseModel):
    id:          int
    brand:       str
    model_name:  str
    loft_angle:  Optional[str] = None
    shaft_type:  str
    description: Optional[str] = None
    price_range: Optional[str] = None

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class RecommendationResponse(BaseModel):
    club_type:     str   # 사용자가 선택한 클럽 종류
    category_name: str   # 시스템이 결정한 세부 카테고리
    reason:        str
    clubs:         List[ClubResponse]
