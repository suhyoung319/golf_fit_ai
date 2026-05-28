from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class SkillLevel(str, enum.Enum):
    beginner = "beginner"          # 입문 (핸디캡 36+)
    amateur = "amateur"            # 아마추어 (핸디캡 18~36)
    intermediate = "intermediate"  # 중급 (핸디캡 10~18)
    advanced = "advanced"          # 상급 (핸디캡 10 미만)


class MissShotType(str, enum.Enum):
    slice = "slice"   # 슬라이스 (오른쪽으로 휨)
    hook = "hook"     # 훅 (왼쪽으로 휨)
    top = "top"       # 탑핑 (공 위를 침)
    fat = "fat"       # 뒤땅
    push = "push"     # 푸시 (오른쪽 직선)
    pull = "pull"     # 풀 (왼쪽 직선)
    none = "none"     # 특별한 미스샷 없음


class SwingSpeed(str, enum.Enum):
    slow = "slow"      # ~85mph 미만
    medium = "medium"  # 85~95mph
    fast = "fast"      # 95mph 초과


class UserGolfProfile(Base):
    __tablename__ = "user_golf_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    skill_level = Column(Enum(SkillLevel), nullable=False)
    miss_shot_type = Column(Enum(MissShotType), nullable=False, default=MissShotType.none)
    distance_avg = Column(Integer, nullable=False, comment="드라이버 평균 비거리 (야드)")
    handicap = Column(Integer, nullable=True, comment="핸디캡 없으면 null")
    swing_speed = Column(Enum(SwingSpeed), nullable=False, default=SwingSpeed.medium)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="profiles")
    recommendations = relationship("Recommendation", back_populates="profile")
