from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.club import Club
from app.models.club_price import ClubPrice
from app.schemas.user_input import (
    DriverInput, WoodInput, UtilityInput,
    IronInput, WedgeInput, PutterInput,
    ClubPriceResponse, Top3Response,
)
from app.services.recommendation import (
    recommend_driver, recommend_wood, recommend_utility,
    recommend_iron, recommend_wedge, recommend_putter,
)

router = APIRouter()


@router.get("/clubs/{club_id}/prices", response_model=list[ClubPriceResponse], summary="클럽 최저가 목록")
def club_prices(club_id: int, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return (
        db.query(ClubPrice)
        .filter(ClubPrice.club_id == club_id)
        .order_by(ClubPrice.price.asc())
        .all()
    )


@router.post("/recommend/driver", response_model=Top3Response, summary="드라이버 Top3 추천",
    description="""
드라이버 Top3 추천. 점수 높은 순으로 카테고리 3개 반환.

```json
{
  "club_type": "driver",
  "handicap": 28,
  "driver_distance": 170,
  "miss_shot": "slice",
  "swing_speed": "slow"
}
```
""")
def driver_recommend(profile: DriverInput, db: Session = Depends(get_db)):
    return recommend_driver(profile, db)


@router.post("/recommend/wood", response_model=Top3Response, summary="페어웨이 우드 Top3 추천",
    description="""
페어웨이 우드 Top3 추천.

```json
{
  "club_type": "wood",
  "handicap": 20,
  "wood_distance": 200,
  "fairway_miss": "thin",
  "trajectory": "high"
}
```
""")
def wood_recommend(profile: WoodInput, db: Session = Depends(get_db)):
    return recommend_wood(profile, db)


@router.post("/recommend/utility", response_model=Top3Response, summary="유틸리티 Top3 추천",
    description="""
유틸리티(하이브리드) Top3 추천.

```json
{
  "club_type": "utility",
  "handicap": 25,
  "utility_distance": 180,
  "long_iron_difficulty": "hard",
  "trajectory": "high"
}
```
""")
def utility_recommend(profile: UtilityInput, db: Session = Depends(get_db)):
    return recommend_utility(profile, db)


@router.post("/recommend/iron", response_model=Top3Response, summary="아이언 Top3 추천",
    description="""
아이언 Top3 추천.

```json
{
  "club_type": "iron",
  "handicap": 18,
  "iron_7_distance": 135,
  "miss_shot": "duff",
  "trajectory": "mid"
}
```
""")
def iron_recommend(profile: IronInput, db: Session = Depends(get_db)):
    return recommend_iron(profile, db)


@router.post("/recommend/wedge", response_model=Top3Response, summary="웨지 Top3 추천",
    description="""
웨지 Top3 추천.

```json
{
  "club_type": "wedge",
  "handicap": 12,
  "approach_distance": 80,
  "wedge_miss": "chunk",
  "spin_need": "high"
}
```
""")
def wedge_recommend(profile: WedgeInput, db: Session = Depends(get_db)):
    return recommend_wedge(profile, db)


@router.post("/recommend/putter", response_model=Top3Response, summary="퍼터 Top3 추천",
    description="""
퍼터 Top3 추천.

```json
{
  "club_type": "putter",
  "handicap": 8,
  "putting_miss": "left",
  "distance_control": "average",
  "stroke_type": "arc"
}
```
""")
def putter_recommend(profile: PutterInput, db: Session = Depends(get_db)):
    return recommend_putter(profile, db)
