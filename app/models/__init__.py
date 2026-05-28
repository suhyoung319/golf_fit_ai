# 모든 모델을 한 곳에서 import해 Base.metadata에 등록.
# seed_data.py 또는 main.py에서 이 파일만 import하면 됨.
from app.models.user import User
from app.models.user_golf_profile import UserGolfProfile
from app.models.club import Club, ClubCategory
from app.models.recommendation import Recommendation, recommendation_clubs

__all__ = [
    "User",
    "UserGolfProfile",
    "Club",
    "ClubCategory",
    "Recommendation",
    "recommendation_clubs",
]
