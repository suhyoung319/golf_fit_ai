from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class ClubType(str, enum.Enum):
    """사용자가 선택하는 클럽 대분류."""
    driver  = "driver"
    wood    = "wood"
    utility = "utility"
    iron    = "iron"
    wedge   = "wedge"
    putter  = "putter"


class ClubCategory(Base):
    """
    클럽 카테고리 — '고반발 드라이버', '포지드 아이언' 등 세부 분류.
    club_type 으로 대분류(driver/iron/wedge…)와 연결됨.
    """
    __tablename__ = "club_categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    club_type   = Column(Enum(ClubType), nullable=False, comment="클럽 대분류")
    target_skill = Column(String(100), nullable=True, comment="추천 대상 실력대")

    clubs = relationship("Club", back_populates="category")


class ShaftType(str, enum.Enum):
    regular     = "regular"
    stiff       = "stiff"
    senior      = "senior"
    extra_stiff = "extra_stiff"
    ladies      = "ladies"


class Club(Base):
    """개별 클럽 모델 — 실제 브랜드·제품 데이터."""
    __tablename__ = "clubs"

    id          = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("club_categories.id"), nullable=False)

    brand       = Column(String(50),  nullable=False)
    model_name  = Column(String(100), nullable=False)
    loft_angle  = Column(String(20),  nullable=True)
    shaft_type  = Column(Enum(ShaftType), nullable=False, default=ShaftType.regular)
    target_user = Column(String(100), nullable=True)
    description = Column(Text,        nullable=True)
    price_range = Column(String(50),  nullable=True)

    category = relationship("ClubCategory", back_populates="clubs")
