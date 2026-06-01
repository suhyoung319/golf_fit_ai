from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 한 유저가 여러 골프 프로필을 가질 수 있음 (재측정 이력 등)
    profiles = relationship("UserGolfProfile", back_populates="user")
