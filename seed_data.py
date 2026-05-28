"""
초기 클럽 데이터 삽입 스크립트.

기존 데이터가 있으면 전부 삭제 후 재삽입합니다 (club_type 컬럼 추가로 인한 재구성).

실행:
    python seed_data.py
"""
from app.db.database import SessionLocal, engine, Base
import app.models  # 모든 모델 Base.metadata 등록


def seed():
    # 테이블 없으면 생성 (신규), 있으면 그대로 진행
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from app.models.club import Club, ClubCategory, ClubType

        # 기존 데이터 초기화 (club_type 컬럼 추가로 재시드 필요)
        existing = db.query(ClubCategory).count()
        if existing > 0:
            print(f"기존 데이터 {existing}개 카테고리 삭제 후 재삽입합니다...")
            db.query(Club).delete()
            db.query(ClubCategory).delete()
            db.commit()

        # ── 카테고리 ─────────────────────────────────────────────
        categories = [
            # driver
            ClubCategory(name="고반발 드라이버", club_type=ClubType.driver,
                         description="관용성 극대화 입문자용",      target_skill="beginner"),
            ClubCategory(name="드라이버",         club_type=ClubType.driver,
                         description="표준 드라이버",               target_skill="intermediate,advanced"),
            # wood
            ClubCategory(name="페어웨이 우드",     club_type=ClubType.wood,
                         description="3번·5번 페어웨이 우드",       target_skill="all"),
            # utility
            ClubCategory(name="하이브리드",        club_type=ClubType.utility,
                         description="롱아이언 대체 하이브리드",     target_skill="all"),
            # iron
            ClubCategory(name="아이언 세트",       club_type=ClubType.iron,
                         description="표준 캐비티백 아이언 세트",    target_skill="beginner,intermediate"),
            ClubCategory(name="포지드 아이언",     club_type=ClubType.iron,
                         description="타구감 중심 단조 아이언",      target_skill="advanced"),
            # wedge
            ClubCategory(name="웨지",              club_type=ClubType.wedge,
                         description="어프로치·벙커 전용",           target_skill="all"),
            # putter
            ClubCategory(name="퍼터",              club_type=ClubType.putter,
                         description="그린 위 퍼팅 전용",            target_skill="all"),
        ]
        db.add_all(categories)
        db.flush()
        cat = {c.name: c.id for c in categories}

        # ── 클럽 데이터 ──────────────────────────────────────────
        clubs = [
            # ── 고반발 드라이버 (beginner / slow~medium)
            Club(category_id=cat["고반발 드라이버"], brand="TaylorMade",
                 model_name="Stealth 2 HD",    shaft_type="regular",
                 loft_angle="12°",   price_range="50만~70만원",
                 target_user="입문자, 슬라이서",
                 description="넓은 페이스와 높은 MOI로 빗맞아도 직진성 유지"),
            Club(category_id=cat["고반발 드라이버"], brand="Callaway",
                 model_name="Paradym MAX",      shaft_type="regular",
                 loft_angle="10.5°", price_range="55만~75만원",
                 target_user="입문자, 거리 부족",
                 description="AI 설계 페이스로 볼 초속 극대화"),
            Club(category_id=cat["고반발 드라이버"], brand="Ping",
                 model_name="G430 MAX",         shaft_type="senior",
                 loft_angle="10.5°", price_range="45만~65만원",
                 target_user="시니어, 입문자",
                 description="업계 최고 수준 MOI — 어디서 맞아도 안정적"),

            # ── 드라이버 (intermediate~advanced / medium~fast)
            Club(category_id=cat["드라이버"], brand="TaylorMade",
                 model_name="Qi10",             shaft_type="stiff",
                 loft_angle="9°",    price_range="60만~80만원",
                 target_user="중급~상급자",
                 description="투어 수준 관용성, 낮은 스핀으로 거리 극대화"),
            Club(category_id=cat["드라이버"], brand="Titleist",
                 model_name="TSR2",             shaft_type="stiff",
                 loft_angle="10°",   price_range="65만~85만원",
                 target_user="중급~상급자",
                 description="정확성과 거리의 균형, 투어 인기 모델"),
            Club(category_id=cat["드라이버"], brand="Cobra",
                 model_name="Aerojet LS",       shaft_type="regular",
                 loft_angle="9°",    price_range="40만~60만원",
                 target_user="중급자",
                 description="에어로다이나믹 헤드로 스윙 저항 최소화"),

            # ── 페어웨이 우드
            Club(category_id=cat["페어웨이 우드"], brand="TaylorMade",
                 model_name="Qi10 3-Wood",      shaft_type="regular",
                 loft_angle="15°",   price_range="28만~42만원",
                 target_user="전 실력대",
                 description="넓은 솔 설계로 탑핑·뒤땅 방지"),
            Club(category_id=cat["페어웨이 우드"], brand="Callaway",
                 model_name="Paradym 3W",       shaft_type="regular",
                 loft_angle="15°",   price_range="30만~45만원",
                 target_user="전 실력대",
                 description="AI 페이스로 페어웨이·러프 모두 대응"),
            Club(category_id=cat["페어웨이 우드"], brand="Ping",
                 model_name="G430 Max 5W",      shaft_type="senior",
                 loft_angle="18°",   price_range="25만~38만원",
                 target_user="시니어, 입문자",
                 description="5번 우드로 롱홀 레이업에 최적"),

            # ── 하이브리드
            Club(category_id=cat["하이브리드"], brand="TaylorMade",
                 model_name="Rescue 2024",      shaft_type="regular",
                 loft_angle="19°",   price_range="22만~35만원",
                 target_user="입문~중급자",
                 description="3번·4번 아이언 대체, 긴 비거리 확보"),
            Club(category_id=cat["하이브리드"], brand="Callaway",
                 model_name="Apex UW",          shaft_type="regular",
                 loft_angle="17°",   price_range="25만~38만원",
                 target_user="입문~중급자",
                 description="페어웨이·러프 활용성 우수한 유틸리티"),
            Club(category_id=cat["하이브리드"], brand="Ping",
                 model_name="G430 Hybrid",      shaft_type="stiff",
                 loft_angle="19°",   price_range="22만~34만원",
                 target_user="중급~상급자",
                 description="저중심 설계로 높은 탄도와 부드러운 착지"),

            # ── 아이언 세트 (beginner~intermediate)
            Club(category_id=cat["아이언 세트"], brand="Mizuno",
                 model_name="JPX923 Hot Metal",  shaft_type="regular",
                 loft_angle="5~PW",  price_range="80만~120만원",
                 target_user="아마추어~중급자",
                 description="고반발 중공 구조로 관용성+비거리 동시 확보"),
            Club(category_id=cat["아이언 세트"], brand="Callaway",
                 model_name="Apex 24",           shaft_type="stiff",
                 loft_angle="5~PW",  price_range="90만~130만원",
                 target_user="중급자",
                 description="AI 페이스 설계로 스윗스팟 넓고 비거리 향상"),
            Club(category_id=cat["아이언 세트"], brand="Ping",
                 model_name="G430 Iron",         shaft_type="regular",
                 loft_angle="5~PW",  price_range="75만~110만원",
                 target_user="아마추어",
                 description="관용성과 타구감을 균형 있게 갖춘 스탠다드"),

            # ── 포지드 아이언 (advanced)
            Club(category_id=cat["포지드 아이언"], brand="Mizuno",
                 model_name="Pro 243",           shaft_type="stiff",
                 loft_angle="4~PW",  price_range="100만~150만원",
                 target_user="상급자",
                 description="연단조 헤드로 업계 최고 수준의 타구감"),
            Club(category_id=cat["포지드 아이언"], brand="Titleist",
                 model_name="T100",              shaft_type="extra_stiff",
                 loft_angle="4~PW",  price_range="110만~160만원",
                 target_user="상급자",
                 description="투어 프로 사용 — 정확성 최우선 설계"),
            Club(category_id=cat["포지드 아이언"], brand="TaylorMade",
                 model_name="P7MB",              shaft_type="stiff",
                 loft_angle="4~PW",  price_range="95만~140만원",
                 target_user="상급자",
                 description="머슬백 단조, 최고의 컨트롤과 타구감"),

            # ── 웨지
            Club(category_id=cat["웨지"], brand="Titleist",
                 model_name="Vokey SM10 56°",   shaft_type="stiff",
                 loft_angle="56°",   price_range="20만~30만원",
                 target_user="중급~상급자",
                 description="모든 라이에서 일관된 스핀과 거리 컨트롤"),
            Club(category_id=cat["웨지"], brand="Cleveland",
                 model_name="RTX6 ZipCore 58°", shaft_type="stiff",
                 loft_angle="58°",   price_range="18만~28만원",
                 target_user="전 실력대",
                 description="ZipCore 기술로 웨트·드라이 조건 모두 높은 스핀"),
            Club(category_id=cat["웨지"], brand="Callaway",
                 model_name="Jaws Raw 60°",     shaft_type="stiff",
                 loft_angle="60°",   price_range="20만~32만원",
                 target_user="중급~상급자",
                 description="날카로운 홈으로 습한 조건에서도 강력한 스핀"),

            # ── 퍼터
            Club(category_id=cat["퍼터"], brand="Odyssey",
                 model_name="White Hot OG #7",  shaft_type="regular",
                 loft_angle="3°",    price_range="20만~35만원",
                 target_user="전 실력대",
                 description="말렛형, 부드러운 타구감과 직진성 우수"),
            Club(category_id=cat["퍼터"], brand="Scotty Cameron",
                 model_name="Phantom X5",       shaft_type="regular",
                 loft_angle="3°",    price_range="60만~90만원",
                 target_user="중급~상급자",
                 description="정밀 CNC 가공 말렛, 정렬선 명확"),
            Club(category_id=cat["퍼터"], brand="Ping",
                 model_name="Anser 2D",         shaft_type="regular",
                 loft_angle="3°",    price_range="25만~40만원",
                 target_user="전 실력대",
                 description="블레이드형 클래식 퍼터, 거리감 조절 탁월"),
        ]
        db.add_all(clubs)
        db.commit()

        print(f"시드 완료: {len(categories)}개 카테고리, {len(clubs)}개 클럽")

    except Exception as e:
        db.rollback()
        print(f"시드 실패: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
