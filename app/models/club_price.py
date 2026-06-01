from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class ClubPrice(Base):
    """클럽별 판매처 가격 정보."""
    __tablename__ = "club_prices"

    id = Column(Integer, primary_key=True, index=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    seller_name = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)
    product_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    club = relationship("Club", back_populates="prices")
