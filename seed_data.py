"""
초기 클럽 데이터 삽입.

실행:
  python seed_data.py

주의:
  기존 테이블에 새 컬럼이 없다면 먼저 README/최종 안내의 ALTER TABLE SQL을 실행하거나
  개발 DB에서 테이블을 재생성한 뒤 실행하세요.
"""
from app.db.database import Base, SessionLocal, engine
import app.models  # noqa: F401 - Base.metadata 모델 등록


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.club import Club, ClubCategory, ClubType, ShaftType

        if db.query(ClubCategory).count() > 0:
            print("기존 데이터 삭제 후 재삽입...")
            db.query(Club).delete()
            db.query(ClubCategory).delete()
            db.commit()

        def category(name, club_type, description, target_skill):
            return ClubCategory(
                name=name,
                club_type=club_type,
                description=description,
                target_skill=target_skill,
            )

        categories = [
            category("고반발 드라이버", ClubType.driver, "MOI 극대화 입문자용", "beginner"),
            category("슬라이스 보정 드라이버", ClubType.driver, "드로우 바이어스 방향 보정", "beginner,intermediate"),
            category("드라이버", ClubType.driver, "표준 드라이버", "intermediate"),
            category("투어 드라이버", ClubType.driver, "저스핀 고볼속 상급자용", "advanced"),
            category("페어웨이 우드", ClubType.wood, "범용 페어웨이 우드", "all"),
            category("로우스핀 우드", ClubType.wood, "낮은 스핀·런 극대화", "intermediate,advanced"),
            category("고탄도 우드", ClubType.wood, "높은 런치·캐리 극대화", "beginner,intermediate"),
            category("하이브리드", ClubType.utility, "롱아이언 대체 범용", "all"),
            category("로우스핀 유틸", ClubType.utility, "낮은 탄도 침투형", "intermediate,advanced"),
            category("고탄도 유틸", ClubType.utility, "높은 탄도 소프트 착지", "beginner,intermediate"),
            category("아이언 세트", ClubType.iron, "캐비티백 관용성", "beginner,intermediate"),
            category("포지드 아이언", ClubType.iron, "단조 타구감 상급자", "advanced"),
            category("게임 임프루브먼트 아이언", ClubType.iron, "두꺼운 솔·넓은 스윗스팟", "beginner"),
            category("웨지", ClubType.wedge, "범용 어프로치·벙커", "all"),
            category("로브 웨지", ClubType.wedge, "고로프트 높은 스핀", "intermediate,advanced"),
            category("갭 웨지", ClubType.wedge, "PW~웨지 거리 공백 충전", "all"),
            category("퍼터", ClubType.putter, "범용 퍼터", "all"),
            category("말렛 퍼터", ClubType.putter, "고MOI 직선 스트로크", "beginner,intermediate"),
            category("블레이드 퍼터", ClubType.putter, "타구감·거리감 상급자", "advanced"),
        ]
        db.add_all(categories)
        db.flush()

        cat_by_name = {c.name: c for c in categories}

        def search_url(brand, model_name):
            query = f"{brand} {model_name}".replace(" ", "+")
            return f"https://www.google.com/search?q={query}+golf+club"

        def club(
            category_name,
            brand,
            model_name,
            shaft_type,
            loft_angle,
            flex,
            forgiveness,
            distance,
            control,
            spin,
            launch,
            handicap_min,
            handicap_max,
            price_range,
            description,
        ):
            category_obj = cat_by_name[category_name]
            return Club(
                category_id=category_obj.id,
                club_type=category_obj.club_type,
                brand=brand,
                model_name=model_name,
                loft_angle=loft_angle,
                shaft_type=shaft_type,
                flex=flex,
                forgiveness_score=forgiveness,
                distance_score=distance,
                control_score=control,
                spin_score=spin,
                launch_type=launch,
                target_handicap_min=handicap_min,
                target_handicap_max=handicap_max,
                price_range=price_range,
                description=description,
                purchase_url=search_url(brand, model_name),
            )

        clubs = [
            club("고반발 드라이버", "TaylorMade", "Stealth 2 HD", ShaftType.regular, "12°", "R", 94, 88, 72, 62, "high", 20, 54, "50만~70만원", "넓은 페이스와 높은 MOI로 빗맞아도 직진성이 좋습니다."),
            club("고반발 드라이버", "Callaway", "Paradym MAX", ShaftType.regular, "10.5°", "R", 92, 90, 74, 64, "high", 18, 54, "55만~75만원", "AI 페이스 기반 반발력과 관용성을 함께 노린 모델입니다."),
            club("고반발 드라이버", "Ping", "G430 MAX", ShaftType.senior, "10.5°", "SR", 96, 84, 76, 66, "mid-high", 20, 54, "45만~65만원", "높은 관용성과 안정적인 탄도로 입문자에게 잘 맞습니다."),
            club("슬라이스 보정 드라이버", "TaylorMade", "Stealth 2 HD Draw", ShaftType.regular, "10.5°", "R", 91, 86, 76, 62, "high", 18, 54, "52만~72만원", "드로우 바이어스 설계로 슬라이스 완화에 초점을 둡니다."),
            club("슬라이스 보정 드라이버", "Callaway", "Paradym Draw", ShaftType.regular, "10.5°", "R", 90, 87, 75, 63, "mid-high", 15, 54, "55만~75만원", "오프셋과 드로우 성향으로 우측 미스를 줄이는 모델입니다."),
            club("슬라이스 보정 드라이버", "Cleveland", "Launcher XL Draw", ShaftType.senior, "10.5°", "SR", 93, 82, 73, 60, "high", 20, 54, "35만~50만원", "큰 헤드와 draw 세팅으로 방향 보정 효과가 큽니다."),
            club("드라이버", "TaylorMade", "Qi10", ShaftType.stiff, "9°", "S", 84, 94, 82, 70, "mid", 5, 28, "60만~80만원", "거리와 관용성의 균형이 좋은 표준 드라이버입니다."),
            club("드라이버", "Titleist", "TSR2", ShaftType.stiff, "10°", "S", 82, 91, 86, 72, "mid", 5, 28, "65만~85만원", "정확성과 볼 스피드 균형을 중시하는 모델입니다."),
            club("드라이버", "Cobra", "Aerojet LS", ShaftType.regular, "9°", "R", 78, 92, 80, 68, "mid-low", 8, 30, "40만~60만원", "빠른 헤드 스피드와 강한 탄도를 노립니다."),
            club("투어 드라이버", "TaylorMade", "Qi10 LS", ShaftType.extra_stiff, "9°", "X", 70, 96, 91, 82, "low", 0, 12, "70만~90만원", "저스핀과 고볼속 중심의 상급자용 모델입니다."),
            club("투어 드라이버", "Titleist", "TSR3", ShaftType.extra_stiff, "9°", "X", 72, 94, 94, 84, "low-mid", 0, 12, "70만~90만원", "탄도와 스핀 조절 폭이 넓은 투어형 드라이버입니다."),
            club("투어 드라이버", "Ping", "G430 LST", ShaftType.stiff, "9°", "S", 76, 92, 90, 80, "low", 0, 15, "60만~80만원", "낮은 스핀으로 강한 구질을 만들기 좋습니다."),
            club("페어웨이 우드", "TaylorMade", "Qi10 3-Wood", ShaftType.regular, "15°", "R", 88, 88, 78, 70, "mid", 10, 54, "28만~42만원", "페어웨이에서 안정적인 런치와 관용성을 제공합니다."),
            club("페어웨이 우드", "Callaway", "Paradym 3W", ShaftType.regular, "15°", "R", 86, 90, 78, 68, "mid", 10, 54, "30만~45만원", "AI 페이스로 볼 초속과 관용성 균형이 좋습니다."),
            club("페어웨이 우드", "Ping", "G430 Max 5W", ShaftType.senior, "18°", "SR", 92, 82, 76, 70, "high", 15, 54, "25만~38만원", "높은 탄도와 편한 런치로 긴 세컨샷에 적합합니다."),
            club("로우스핀 우드", "TaylorMade", "Qi10 LS 3W", ShaftType.stiff, "13.5°", "S", 72, 92, 88, 82, "low", 0, 18, "32만~48만원", "낮은 스핀과 강한 침투 탄도를 노리는 우드입니다."),
            club("로우스핀 우드", "Titleist", "TSR2 3W", ShaftType.stiff, "15°", "S", 76, 90, 86, 80, "low-mid", 0, 18, "35만~50만원", "상급자의 탄도 제어와 거리 확보에 잘 맞습니다."),
            club("로우스핀 우드", "Cobra", "Aerojet LS 3W", ShaftType.extra_stiff, "14.5°", "X", 70, 93, 88, 82, "low", 0, 15, "30만~45만원", "빠른 스윙에 맞춘 저스핀 페어웨이 우드입니다."),
            club("고탄도 우드", "Callaway", "Paradym MAX 5W", ShaftType.regular, "18°", "R", 90, 84, 76, 72, "high", 15, 54, "28만~42만원", "높은 런치각으로 캐리 거리를 확보합니다."),
            club("고탄도 우드", "Ping", "G430 MAX 7W", ShaftType.senior, "21°", "SR", 94, 80, 74, 72, "high", 18, 54, "25만~38만원", "느린 스윙에서도 쉽게 뜨는 7번 우드입니다."),
            club("고탄도 우드", "Cleveland", "Launcher XL Halo 5W", ShaftType.regular, "18°", "R", 92, 82, 72, 70, "high", 18, 54, "22만~35만원", "넓은 솔과 높은 탄도로 미스샷 부담을 줄입니다."),
            club("하이브리드", "TaylorMade", "Rescue 2024", ShaftType.regular, "19°", "R", 88, 86, 78, 70, "high", 10, 54, "22만~35만원", "롱아이언 대체용으로 편하게 띄우기 좋은 모델입니다."),
            club("하이브리드", "Callaway", "Apex UW", ShaftType.regular, "17°", "R", 84, 88, 82, 70, "mid-high", 8, 36, "25만~38만원", "페어웨이와 러프에서 활용성이 높은 유틸리티입니다."),
            club("하이브리드", "Ping", "G430 Hybrid", ShaftType.stiff, "19°", "S", 90, 84, 80, 72, "high", 8, 40, "22만~34만원", "저중심 설계로 높은 탄도와 안정감을 제공합니다."),
            club("로우스핀 유틸", "TaylorMade", "P790 UDI", ShaftType.stiff, "18°", "S", 68, 90, 90, 82, "low", 0, 18, "30만~45만원", "아이언형 유틸로 낮고 강한 탄도에 적합합니다."),
            club("로우스핀 유틸", "Titleist", "U505 Utility", ShaftType.stiff, "18°", "S", 72, 88, 88, 80, "low-mid", 0, 18, "28만~42만원", "투어형 제어와 유틸 관용성을 결합한 모델입니다."),
            club("로우스핀 유틸", "Srixon", "ZX Utility", ShaftType.extra_stiff, "20°", "X", 70, 86, 90, 78, "low", 0, 15, "25만~38만원", "롱아이언 숙련자에게 맞는 침투형 유틸입니다."),
            club("고탄도 유틸", "Callaway", "Apex UW Hi", ShaftType.regular, "21°", "R", 88, 84, 78, 72, "high", 12, 54, "25만~38만원", "높은 런치와 소프트한 착지를 돕습니다."),
            club("고탄도 유틸", "Cleveland", "Launcher XL Halo", ShaftType.regular, "19°", "R", 94, 80, 72, 70, "high", 18, 54, "20만~32만원", "광폭 솔로 쉽게 뜨고 관용성이 큽니다."),
            club("고탄도 유틸", "Ping", "G430 HL Hybrid", ShaftType.senior, "22°", "SR", 92, 80, 74, 72, "high", 18, 54, "24만~36만원", "가벼운 세팅과 높은 탄도로 긴 샷 부담을 줄입니다."),
            club("아이언 세트", "Mizuno", "JPX923 Hot Metal", ShaftType.regular, "5~PW", "R", 88, 88, 80, 72, "mid-high", 10, 36, "80만~120만원", "고반발 중공 구조로 관용성과 비거리가 좋습니다."),
            club("아이언 세트", "Callaway", "Apex 24", ShaftType.stiff, "5~PW", "S", 82, 86, 86, 74, "mid", 5, 28, "90만~130만원", "타구감과 비거리 균형이 좋은 아이언 세트입니다."),
            club("아이언 세트", "Ping", "G430 Iron", ShaftType.regular, "5~PW", "R", 90, 84, 80, 72, "mid-high", 10, 40, "75만~110만원", "관용성과 안정적인 탄도를 제공하는 스탠다드 아이언입니다."),
            club("포지드 아이언", "Mizuno", "Pro 243", ShaftType.stiff, "4~PW", "S", 70, 82, 94, 78, "mid", 0, 12, "100만~150만원", "연단조 타구감과 컨트롤 성능이 강점입니다."),
            club("포지드 아이언", "Titleist", "T100", ShaftType.extra_stiff, "4~PW", "X", 66, 80, 96, 80, "mid-low", 0, 10, "110만~160만원", "정확한 거리 제어를 원하는 상급자용 아이언입니다."),
            club("포지드 아이언", "TaylorMade", "P7MC", ShaftType.stiff, "4~PW", "S", 68, 80, 94, 78, "mid", 0, 12, "95만~140만원", "컴팩트한 헤드와 정교한 조작성에 초점을 둡니다."),
            club("게임 임프루브먼트 아이언", "TaylorMade", "SIM2 Max OS", ShaftType.regular, "5~PW", "R", 94, 86, 70, 68, "high", 18, 54, "65만~95만원", "두꺼운 솔과 넓은 스윗스팟으로 실수를 줄입니다."),
            club("게임 임프루브먼트 아이언", "Cleveland", "Launcher XL Iron", ShaftType.regular, "5~PW", "R", 96, 82, 68, 66, "high", 20, 54, "55만~80만원", "입문자에게 필요한 관용성을 크게 높인 아이언입니다."),
            club("게임 임프루브먼트 아이언", "Callaway", "Big Bertha Iron", ShaftType.senior, "5~PW", "SR", 95, 84, 68, 66, "high", 20, 54, "70만~105만원", "쉽게 뜨고 멀리 가도록 설계된 GI 아이언입니다."),
            club("웨지", "Titleist", "Vokey SM10 56°", ShaftType.stiff, "56°", "S", 74, 65, 92, 92, "mid", 0, 54, "20만~30만원", "다양한 라이에서 일관된 스핀과 컨트롤을 제공합니다."),
            club("웨지", "Cleveland", "RTX6 ZipCore 58°", ShaftType.stiff, "58°", "S", 78, 64, 90, 94, "mid-high", 0, 54, "18만~28만원", "웨트 조건에서도 높은 스핀을 노릴 수 있습니다."),
            club("웨지", "Callaway", "Jaws Raw 60°", ShaftType.stiff, "60°", "S", 72, 62, 91, 95, "high", 0, 54, "20만~32만원", "날카로운 그루브로 강한 스핀을 만드는 웨지입니다."),
            club("로브 웨지", "Titleist", "Vokey SM10 60°", ShaftType.stiff, "60°", "S", 68, 58, 94, 96, "high", 0, 20, "22만~32만원", "짧은 어프로치와 높은 탄도 샷에 특화됐습니다."),
            club("로브 웨지", "Cleveland", "RTX6 Full Face 58°", ShaftType.stiff, "58°", "S", 74, 60, 90, 94, "high", 5, 28, "20만~30만원", "풀페이스 홈으로 오픈 페이스 샷 안정성이 좋습니다."),
            club("로브 웨지", "Callaway", "Jaws Raw Full Toe 60°", ShaftType.stiff, "60°", "S", 70, 58, 92, 96, "high", 0, 22, "22만~34만원", "높은 로프트와 강한 스핀으로 빠른 정지를 돕습니다."),
            club("갭 웨지", "Titleist", "Vokey SM10 50°", ShaftType.stiff, "50°", "S", 78, 68, 90, 88, "mid", 0, 54, "20만~30만원", "PW 이후 거리 공백을 안정적으로 채웁니다."),
            club("갭 웨지", "Cleveland", "RTX6 52°", ShaftType.stiff, "52°", "S", 80, 66, 88, 90, "mid", 0, 54, "18만~26만원", "100야드 안쪽 거리 조절이 쉬운 갭 웨지입니다."),
            club("갭 웨지", "Callaway", "Jaws Raw 50°", ShaftType.regular, "50°", "R", 76, 68, 88, 88, "mid", 5, 54, "20만~32만원", "중거리 어프로치에서 스핀과 런을 균형 있게 제공합니다."),
            club("퍼터", "Odyssey", "White Hot OG #7", ShaftType.regular, "3°", "Standard", 88, 40, 86, 50, "mid", 0, 54, "20만~35만원", "부드러운 타구감과 높은 직진성을 제공하는 범용 퍼터입니다."),
            club("퍼터", "TaylorMade", "Spider GT", ShaftType.regular, "3°", "Standard", 90, 40, 84, 50, "mid", 0, 54, "25만~40만원", "정렬 보조와 관용성이 좋은 말렛형 퍼터입니다."),
            club("퍼터", "Ping", "Anser 2023", ShaftType.regular, "3°", "Standard", 78, 40, 90, 50, "mid", 0, 54, "25만~40만원", "클래식한 감각과 거리감이 좋은 범용 퍼터입니다."),
            club("말렛 퍼터", "Scotty Cameron", "Phantom X5", ShaftType.regular, "3°", "Standard", 92, 40, 88, 50, "mid", 0, 36, "60만~90만원", "명확한 정렬선과 높은 MOI를 가진 말렛 퍼터입니다."),
            club("말렛 퍼터", "Cleveland", "Frontline Elite Cero", ShaftType.regular, "3°", "Standard", 94, 40, 84, 50, "mid", 10, 54, "22만~35만원", "직선 스트로크와 방향성 보정에 강점이 있습니다."),
            club("말렛 퍼터", "Odyssey", "Eleven Tour Lined", ShaftType.regular, "3°", "Standard", 93, 40, 86, 50, "mid", 5, 54, "30만~45만원", "큰 헤드 안정성과 쉬운 정렬을 제공합니다."),
            club("블레이드 퍼터", "Scotty Cameron", "Newport 2", ShaftType.regular, "3.5°", "Standard", 70, 40, 96, 50, "mid", 0, 12, "70만~100만원", "섬세한 타구감과 거리감을 원하는 상급자에게 적합합니다."),
            club("블레이드 퍼터", "Ping", "Anser 2D", ShaftType.regular, "3°", "Standard", 76, 40, 92, 50, "mid", 0, 18, "25만~40만원", "아크 스트로크와 클래식한 조작감에 잘 맞습니다."),
            club("블레이드 퍼터", "Odyssey", "Tri-Hot 5K One", ShaftType.regular, "3°", "Standard", 78, 40, 90, 50, "mid", 0, 20, "35만~55만원", "블레이드 감각에 안정성을 더한 퍼터입니다."),
        ]

        db.add_all(clubs)
        db.commit()
        print(f"시드 완료: {len(categories)}개 카테고리 / {len(clubs)}개 클럽")

    except Exception as exc:
        db.rollback()
        print(f"시드 실패: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
