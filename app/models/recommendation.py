from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


# 추천-클럽 다대다 연결 테이블
recommendation_clubs = Table(
    "recommendation_clubs",
    Base.metadata,
    Column("recommendation_id", Integer, ForeignKey("recommendations.id"), primary_key=True),
    Column("club_id", Integer, ForeignKey("clubs.id"), primary_key=True),
)


class Recommendation(Base):
    """추천 결과 저장 — 이력 추적 및 추후 ML 학습 데이터로 활용."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_golf_profiles.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("club_categories.id"), nullable=False)
    reason = Column(Text, nullable=True, comment="추천 이유 설명 텍스트")
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserGolfProfile", back_populates="recommendations")
    category = relationship("ClubCategory")
    clubs = relationship("Club", secondary=recommendation_clubs)
