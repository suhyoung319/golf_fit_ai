"""
club_type별 입력 스키마 + Top3 응답 스키마.

입력: club_type별 독립 스키마 (6종)
응답: RecommendationItem (rank/score/matched_traits/reason/clubs) × 3 → Top3Response
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


# ── 공용 Enum ────────────────────────────────────────────────────

class SwingSpeed(str, Enum):
    slow   = "slow"
    medium = "medium"
    fast   = "fast"

class Trajectory(str, Enum):
    low  = "low"
    mid  = "mid"
    high = "high"

class StrokeType(str, Enum):
    straight = "straight"
    arc      = "arc"


# ── club_type별 입력 스키마 ──────────────────────────────────────

class DriverInput(BaseModel):
    club_type:       Literal["driver"]
    handicap:        int        = Field(..., ge=0, le=54)
    driver_distance: int        = Field(..., ge=50, le=400, description="드라이버 평균 비거리 (야드)")
    miss_shot:       Literal["slice", "hook", "high", "low", "none"] = "none"
    swing_speed:     SwingSpeed = SwingSpeed.medium
    model_config = {"use_enum_values": True}

class WoodInput(BaseModel):
    club_type:     Literal["wood"]
    handicap:      int        = Field(..., ge=0, le=54)
    wood_distance: int        = Field(..., ge=30, le=300, description="페어웨이 우드 평균 비거리 (야드)")
    fairway_miss:  Literal["thin", "fat", "left", "right", "none"] = "none"
    trajectory:    Trajectory = Trajectory.mid
    model_config = {"use_enum_values": True}

class UtilityInput(BaseModel):
    club_type:            Literal["utility"]
    handicap:             int        = Field(..., ge=0, le=54)
    utility_distance:     int        = Field(..., ge=30, le=280, description="유틸리티 평균 비거리 (야드)")
    long_iron_difficulty: Literal["very_hard", "hard", "ok"] = "hard"
    trajectory:           Trajectory = Trajectory.mid
    model_config = {"use_enum_values": True}

class IronInput(BaseModel):
    club_type:       Literal["iron"]
    handicap:        int        = Field(..., ge=0, le=54)
    iron_7_distance: int        = Field(..., ge=50, le=220, description="7번 아이언 평균 비거리 (야드)")
    miss_shot:       Literal["top", "duff", "pull", "push", "none"] = "none"
    trajectory:      Trajectory = Trajectory.mid
    model_config = {"use_enum_values": True}

class WedgeInput(BaseModel):
    club_type:         Literal["wedge"]
    handicap:          int     = Field(..., ge=0, le=54)
    approach_distance: int     = Field(..., ge=10, le=150, description="주요 어프로치 거리 (야드)")
    wedge_miss:        Literal["short", "long", "skull", "chunk", "none"] = "none"
    spin_need:         Literal["high", "medium", "low"] = "medium"
    model_config = {"use_enum_values": True}

class PutterInput(BaseModel):
    club_type:        Literal["putter"]
    handicap:         int        = Field(..., ge=0, le=54)
    putting_miss:     Literal["short", "long", "left", "right", "none"] = "none"
    distance_control: Literal["poor", "average", "good"] = "average"
    stroke_type:      StrokeType = StrokeType.arc
    model_config = {"use_enum_values": True}


# ── 응답 스키마 ──────────────────────────────────────────────────

class ClubResponse(BaseModel):
    id:          int
    brand:       str
    model_name:  str
    loft_angle:  Optional[str] = None
    shaft_type:  str
    description: Optional[str] = None
    price_range: Optional[str] = None
    model_config = {"from_attributes": True, "protected_namespaces": ()}


class RecommendationItem(BaseModel):
    """단일 추천 항목 — rank·score·matched_traits·reason·clubs 포함."""
    rank:           int
    category_name:  str
    score:          int                  # 0~100 룰 기반 가중치 점수
    reason:         str
    matched_traits: List[str]            # 점수 산출 근거 trait 목록
    clubs:          List[ClubResponse]


class Top3Response(BaseModel):
    """최종 API 응답 — Top3 추천 목록 포함."""
    club_type:        str
    handicap:         int
    calculated_skill: str                # handicap 기반 자동 계산값
    recommendations:  List[RecommendationItem]
