"""
초기 클럽 데이터 삽입.
Top3 추천을 위해 club_type별 카테고리를 3개씩 확장.

실행: python seed_data.py
"""
from app.db.database import SessionLocal, engine, Base
import app.models


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.club import Club, ClubCategory, ClubType

        if db.query(ClubCategory).count() > 0:
            print("기존 데이터 삭제 후 재삽입...")
            db.query(Club).delete()
            db.query(ClubCategory).delete()
            db.commit()

        # ── 카테고리 (club_type별 3개씩 = 총 18개) ──────────────
        categories = [
            # driver (3)
            ClubCategory(name="고반발 드라이버",      club_type=ClubType.driver,
                         description="MOI 극대화 입문자용",         target_skill="beginner"),
            ClubCategory(name="슬라이스 보정 드라이버", club_type=ClubType.driver,
                         description="드로우 바이어스 방향 보정",   target_skill="beginner,intermediate"),
            ClubCategory(name="드라이버",               club_type=ClubType.driver,
                         description="표준 드라이버",               target_skill="intermediate"),
            ClubCategory(name="투어 드라이버",          club_type=ClubType.driver,
                         description="저스핀 고볼속 상급자용",      target_skill="advanced"),

            # wood (3)
            ClubCategory(name="페어웨이 우드",  club_type=ClubType.wood,
                         description="범용 페어웨이 우드",          target_skill="all"),
            ClubCategory(name="로우스핀 우드",  club_type=ClubType.wood,
                         description="낮은 스핀·런 극대화",         target_skill="intermediate,advanced"),
            ClubCategory(name="고탄도 우드",    club_type=ClubType.wood,
                         description="높은 런치·캐리 극대화",       target_skill="beginner,intermediate"),

            # utility (3)
            ClubCategory(name="하이브리드",    club_type=ClubType.utility,
                         description="롱아이언 대체 범용",           target_skill="all"),
            ClubCategory(name="로우스핀 유틸", club_type=ClubType.utility,
                         description="낮은 탄도 침투형",             target_skill="intermediate,advanced"),
            ClubCategory(name="고탄도 유틸",   club_type=ClubType.utility,
                         description="높은 탄도 소프트 착지",        target_skill="beginner,intermediate"),

            # iron (3)
            ClubCategory(name="아이언 세트",              club_type=ClubType.iron,
                         description="캐비티백 관용성",              target_skill="beginner,intermediate"),
            ClubCategory(name="포지드 아이언",            club_type=ClubType.iron,
                         description="단조 타구감 상급자",           target_skill="advanced"),
            ClubCategory(name="게임 임프루브먼트 아이언", club_type=ClubType.iron,
                         description="두꺼운 솔·넓은 스윗스팟",     target_skill="beginner"),

            # wedge (3)
            ClubCategory(name="웨지",     club_type=ClubType.wedge,
                         description="범용 어프로치·벙커",           target_skill="all"),
            ClubCategory(name="로브 웨지", club_type=ClubType.wedge,
                         description="고로프트 높은 스핀",           target_skill="intermediate,advanced"),
            ClubCategory(name="갭 웨지",   club_type=ClubType.wedge,
                         description="PW~웨지 거리 공백 충전",       target_skill="all"),

            # putter (3)
            ClubCategory(name="퍼터",        club_type=ClubType.putter,
                         description="범용 퍼터",                    target_skill="all"),
            ClubCategory(name="말렛 퍼터",   club_type=ClubType.putter,
                         description="고MOI 직선 스트로크",           target_skill="beginner,intermediate"),
            ClubCategory(name="블레이드 퍼터", club_type=ClubType.putter,
                         description="타구감·거리감 상급자",          target_skill="advanced"),
        ]
        db.add_all(categories)
        db.flush()
        cat = {c.name: c.id for c in categories}

        # ── 클럽 데이터 ────────────────────────────────────────────
        clubs = [
            # ── 고반발 드라이버
            Club(category_id=cat["고반발 드라이버"], brand="TaylorMade",
                 model_name="Stealth 2 HD",    shaft_type="regular", loft_angle="12°",
                 price_range="50만~70만원",    description="넓은 페이스·높은 MOI — 빗맞아도 직진"),
            Club(category_id=cat["고반발 드라이버"], brand="Callaway",
                 model_name="Paradym MAX",     shaft_type="regular", loft_angle="10.5°",
                 price_range="55만~75만원",    description="AI 페이스로 볼 초속 극대화"),
            Club(category_id=cat["고반발 드라이버"], brand="Ping",
                 model_name="G430 MAX",        shaft_type="senior",  loft_angle="10.5°",
                 price_range="45만~65만원",    description="업계 최고 MOI — 어디서 맞아도 안정"),

            # ── 슬라이스 보정 드라이버
            Club(category_id=cat["슬라이스 보정 드라이버"], brand="TaylorMade",
                 model_name="Stealth 2 HD Draw", shaft_type="regular", loft_angle="10.5°",
                 price_range="52만~72만원",    description="드로우 바이어스 — 슬라이스를 구조적으로 보정"),
            Club(category_id=cat["슬라이스 보정 드라이버"], brand="Callaway",
                 model_name="Paradym Draw",    shaft_type="regular", loft_angle="10.5°",
                 price_range="55만~75만원",    description="오프셋 + 드로우 바이어스 페이스"),
            Club(category_id=cat["슬라이스 보정 드라이버"], brand="Cleveland",
                 model_name="Launcher XL Draw", shaft_type="regular", loft_angle="10.5°",
                 price_range="35만~50만원",    description="Draw 전용 설계로 방향 교정 효과 탁월"),

            # ── 드라이버
            Club(category_id=cat["드라이버"], brand="TaylorMade",
                 model_name="Qi10",            shaft_type="stiff",   loft_angle="9°",
                 price_range="60만~80만원",    description="낮은 스핀·높은 볼속으로 거리 극대화"),
            Club(category_id=cat["드라이버"], brand="Titleist",
                 model_name="TSR2",            shaft_type="stiff",   loft_angle="10°",
                 price_range="65만~85만원",    description="정확성과 거리 균형 — 투어 인기 모델"),
            Club(category_id=cat["드라이버"], brand="Cobra",
                 model_name="Aerojet LS",      shaft_type="regular", loft_angle="9°",
                 price_range="40만~60만원",    description="에어로다이나믹 헤드로 스윙 저항 최소화"),

            # ── 투어 드라이버
            Club(category_id=cat["투어 드라이버"], brand="TaylorMade",
                 model_name="Qi10 LS",         shaft_type="extra_stiff", loft_angle="9°",
                 price_range="70만~90만원",    description="저스핀·고볼속 — 투어 프로 설계"),
            Club(category_id=cat["투어 드라이버"], brand="Titleist",
                 model_name="TSR3",            shaft_type="extra_stiff", loft_angle="9°",
                 price_range="70만~90만원",    description="조정 가중추로 탄도·스핀 세밀 조절"),
            Club(category_id=cat["투어 드라이버"], brand="Ping",
                 model_name="G430 LST",        shaft_type="stiff",   loft_angle="9°",
                 price_range="60만~80만원",    description="저스핀 투어 드라이버"),

            # ── 페어웨이 우드
            Club(category_id=cat["페어웨이 우드"], brand="TaylorMade",
                 model_name="Qi10 3-Wood",     shaft_type="regular", loft_angle="15°",
                 price_range="28만~42만원",    description="넓은 솔로 탑핑·뒤땅 방지"),
            Club(category_id=cat["페어웨이 우드"], brand="Callaway",
                 model_name="Paradym 3W",      shaft_type="regular", loft_angle="15°",
                 price_range="30만~45만원",    description="AI 페이스로 볼 초속 향상"),
            Club(category_id=cat["페어웨이 우드"], brand="Ping",
                 model_name="G430 Max 5W",     shaft_type="senior",  loft_angle="18°",
                 price_range="25만~38만원",    description="5번 우드 — 롱홀 레이업 최적"),

            # ── 로우스핀 우드
            Club(category_id=cat["로우스핀 우드"], brand="TaylorMade",
                 model_name="Qi10 LS 3W",      shaft_type="stiff",   loft_angle="13.5°",
                 price_range="32만~48만원",    description="낮은 스핀·강한 침투 탄도"),
            Club(category_id=cat["로우스핀 우드"], brand="Titleist",
                 model_name="TSR2 3W",         shaft_type="stiff",   loft_angle="15°",
                 price_range="35만~50만원",    description="저스핀 투어 페어웨이 우드"),

            # ── 고탄도 우드
            Club(category_id=cat["고탄도 우드"], brand="Callaway",
                 model_name="Paradym MAX 5W",  shaft_type="regular", loft_angle="18°",
                 price_range="28만~42만원",    description="높은 런치각·소프트 착지"),
            Club(category_id=cat["고탄도 우드"], brand="Ping",
                 model_name="G430 MAX 7W",     shaft_type="senior",  loft_angle="21°",
                 price_range="25만~38만원",    description="7번 우드 — 시니어·여성에 최적"),

            # ── 하이브리드
            Club(category_id=cat["하이브리드"], brand="TaylorMade",
                 model_name="Rescue 2024",     shaft_type="regular", loft_angle="19°",
                 price_range="22만~35만원",    description="3·4번 아이언 대체 — 높은 탄도"),
            Club(category_id=cat["하이브리드"], brand="Callaway",
                 model_name="Apex UW",         shaft_type="regular", loft_angle="17°",
                 price_range="25만~38만원",    description="페어웨이·러프 활용성 우수"),
            Club(category_id=cat["하이브리드"], brand="Ping",
                 model_name="G430 Hybrid",     shaft_type="stiff",   loft_angle="19°",
                 price_range="22만~34만원",    description="저중심 설계 — 높은 탄도·부드러운 착지"),

            # ── 로우스핀 유틸
            Club(category_id=cat["로우스핀 유틸"], brand="TaylorMade",
                 model_name="P790 UDI",        shaft_type="stiff",   loft_angle="18°",
                 price_range="30만~45만원",    description="아이언형 유틸 — 낮은 탄도·강한 침투"),
            Club(category_id=cat["로우스핀 유틸"], brand="Titleist",
                 model_name="U505 Utility",    shaft_type="stiff",   loft_angle="18°",
                 price_range="28만~42만원",    description="저스핀·투어 퍼포먼스 유틸리티"),

            # ── 고탄도 유틸
            Club(category_id=cat["고탄도 유틸"], brand="Callaway",
                 model_name="Apex UW Hi",      shaft_type="regular", loft_angle="21°",
                 price_range="25만~38만원",    description="높은 런치·소프트 착지 하이브리드"),
            Club(category_id=cat["고탄도 유틸"], brand="Cleveland",
                 model_name="Launcher XL Halo", shaft_type="regular", loft_angle="19°",
                 price_range="20만~32만원",    description="광폭 솔로 탄도·관용성 극대화"),

            # ── 아이언 세트
            Club(category_id=cat["아이언 세트"], brand="Mizuno",
                 model_name="JPX923 Hot Metal",shaft_type="regular", loft_angle="5~PW",
                 price_range="80만~120만원",   description="고반발 중공 — 관용성·비거리 동시 확보"),
            Club(category_id=cat["아이언 세트"], brand="Callaway",
                 model_name="Apex 24",         shaft_type="stiff",   loft_angle="5~PW",
                 price_range="90만~130만원",   description="AI 페이스로 스윗스팟 넓고 비거리 향상"),
            Club(category_id=cat["아이언 세트"], brand="Ping",
                 model_name="G430 Iron",       shaft_type="regular", loft_angle="5~PW",
                 price_range="75만~110만원",   description="관용성·타구감 균형 스탠다드"),

            # ── 포지드 아이언
            Club(category_id=cat["포지드 아이언"], brand="Mizuno",
                 model_name="Pro 243",         shaft_type="stiff",       loft_angle="4~PW",
                 price_range="100만~150만원",  description="연단조 — 업계 최고 타구감"),
            Club(category_id=cat["포지드 아이언"], brand="Titleist",
                 model_name="T100",            shaft_type="extra_stiff", loft_angle="4~PW",
                 price_range="110만~160만원",  description="투어 프로 사용 — 정확성 최우선"),
            Club(category_id=cat["포지드 아이언"], brand="TaylorMade",
                 model_name="P7MB",            shaft_type="stiff",       loft_angle="4~PW",
                 price_range="95만~140만원",   description="머슬백 단조 — 최고의 컨트롤"),

            # ── 게임 임프루브먼트 아이언
            Club(category_id=cat["게임 임프루브먼트 아이언"], brand="TaylorMade",
                 model_name="SIM2 Max OS",     shaft_type="regular", loft_angle="5~PW",
                 price_range="65만~95만원",    description="두꺼운 솔·넓은 스윗스팟으로 뒤땅 방지"),
            Club(category_id=cat["게임 임프루브먼트 아이언"], brand="Cleveland",
                 model_name="Launcher XL Iron", shaft_type="regular", loft_angle="5~PW",
                 price_range="55만~80만원",    description="GI 아이언 중 최상위 관용성"),

            # ── 웨지
            Club(category_id=cat["웨지"], brand="Titleist",
                 model_name="Vokey SM10 56°",  shaft_type="stiff",   loft_angle="56°",
                 price_range="20만~30만원",    description="모든 라이 일관된 스핀·거리 컨트롤"),
            Club(category_id=cat["웨지"], brand="Cleveland",
                 model_name="RTX6 ZipCore 58°", shaft_type="stiff",  loft_angle="58°",
                 price_range="18만~28만원",    description="ZipCore — 웨트·드라이 높은 스핀"),
            Club(category_id=cat["웨지"], brand="Callaway",
                 model_name="Jaws Raw 60°",    shaft_type="stiff",   loft_angle="60°",
                 price_range="20만~32만원",    description="날카로운 홈 — 습한 조건 강력 스핀"),

            # ── 로브 웨지
            Club(category_id=cat["로브 웨지"], brand="Titleist",
                 model_name="Vokey SM10 60°",  shaft_type="stiff",   loft_angle="60°",
                 price_range="22만~32만원",    description="60도 로브 웨지 — 피치샷 전문"),
            Club(category_id=cat["로브 웨지"], brand="Cleveland",
                 model_name="RTX6 Full Face 58°", shaft_type="stiff", loft_angle="58°",
                 price_range="20만~30만원",    description="풀페이스 홈 — 오픈 페이스 전구간 스핀"),

            # ── 갭 웨지
            Club(category_id=cat["갭 웨지"], brand="Titleist",
                 model_name="Vokey SM10 50°",  shaft_type="stiff",   loft_angle="50°",
                 price_range="20만~30만원",    description="갭 웨지 50도 — PW 이후 거리 공백 충전"),
            Club(category_id=cat["갭 웨지"], brand="Cleveland",
                 model_name="RTX6 52°",        shaft_type="stiff",   loft_angle="52°",
                 price_range="18만~26만원",    description="52도 갭 웨지 — 100야드 안쪽 거리 조절"),

            # ── 퍼터
            Club(category_id=cat["퍼터"], brand="Odyssey",
                 model_name="White Hot OG #7", shaft_type="regular", loft_angle="3°",
                 price_range="20만~35만원",    description="말렛형 — 부드러운 타구감·직진성 우수"),
            Club(category_id=cat["퍼터"], brand="TaylorMade",
                 model_name="Spider GT",       shaft_type="regular", loft_angle="3°",
                 price_range="25만~40만원",    description="스파이더 — 정렬 보조·관용성 높은 말렛"),

            # ── 말렛 퍼터
            Club(category_id=cat["말렛 퍼터"], brand="Scotty Cameron",
                 model_name="Phantom X5",      shaft_type="regular", loft_angle="3°",
                 price_range="60만~90만원",    description="정밀 CNC 가공 말렛 — 정렬선 명확"),
            Club(category_id=cat["말렛 퍼터"], brand="Cleveland",
                 model_name="Frontline Elite Cero", shaft_type="regular", loft_angle="3°",
                 price_range="22만~35만원",    description="전면 가중 말렛 — 직선 스트로크 최적"),

            # ── 블레이드 퍼터
            Club(category_id=cat["블레이드 퍼터"], brand="Scotty Cameron",
                 model_name="Phantom X 5S",    shaft_type="regular", loft_angle="3.5°",
                 price_range="70만~100만원",   description="블레이드형 — 타구감·거리감 최고"),
            Club(category_id=cat["블레이드 퍼터"], brand="Ping",
                 model_name="Anser 2D",        shaft_type="regular", loft_angle="3°",
                 price_range="25만~40만원",    description="클래식 블레이드 — 아크 스트로크 탁월"),
        ]
        db.add_all(clubs)
        db.commit()
        print(f"시드 완료: {len(categories)}개 카테고리 / {len(clubs)}개 클럽")

    except Exception as e:
        db.rollback()
        print(f"시드 실패: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
