"""
club_type + category_name + matched_traits 기반 추천 이유 생성.
Top3 각각 다른 이유 텍스트를 만들기 위해 category_name도 활용.
"""

def _skill_label(handicap: int) -> str:
    if handicap >= 25: return "입문자"
    if handicap >= 10: return "중급자"
    return "상급자"

SWING_KO  = {"slow": "느린", "medium": "보통", "fast": "빠른"}
TRAJ_KO   = {"low": "낮은", "mid": "중간", "high": "높은"}
STROKE_KO = {"straight": "직선", "arc": "아크"}

DRIVER_MISS_KO  = {"slice":"슬라이스", "hook":"훅", "high":"높은탄도", "low":"낮은탄도", "none": None}
IRON_MISS_KO    = {"top":"탑핑", "duff":"뒤땅", "pull":"풀", "push":"푸시", "none": None}
WEDGE_MISS_KO   = {"short":"짧음", "long":"길게 넘어감", "skull":"스컬", "chunk":"청크", "none": None}
FAIRWAY_MISS_KO = {"thin":"얇게 맞음", "fat":"뒤땅", "left":"왼쪽", "right":"오른쪽", "none": None}
PUTTING_MISS_KO = {"short":"짧음", "long":"길게 넘어감", "left":"왼쪽", "right":"오른쪽", "none": None}
LONG_IRON_KO    = {"very_hard":"매우 어려움", "hard":"어려움", "ok":"무난함"}
SPIN_KO         = {"high":"높은 스핀", "medium":"중간 스핀", "low":"낮은 스핀"}
DIST_CTRL_KO    = {"poor":"거리감 부족", "average":"보통", "good":"거리감 양호"}


# ── 드라이버 ─────────────────────────────────────────────────────

_DRIVER_REASON = {
    "고반발 드라이버":    "관용성과 반발력이 높아 빗맞아도 직진성이 유지됩니다. 슬로우 스윙과 미스샷이 잦은 경우에 특히 효과적입니다.",
    "슬라이스 보정 드라이버": "드로우 바이어스 페이스 설계로 슬라이스를 구조적으로 보정합니다. 방향성 문제가 잦은 입문~아마추어에게 적합합니다.",
    "드라이버":           "표준 드라이버로 관용성과 거리를 균형 있게 제공합니다. 중급 이상의 플레이어에게 적합합니다.",
    "투어 드라이버":      "낮은 스핀과 강한 볼 스피드로 거리를 극대화합니다. 빠른 스윙 속도와 일관된 임팩트를 가진 상급자용입니다.",
}

def build_driver_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill = _skill_label(profile.handicap)
    miss  = DRIVER_MISS_KO.get(profile.miss_shot)
    swing = SWING_KO.get(profile.swing_speed, "")
    base  = _DRIVER_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = f"핸디캡 {profile.handicap}({skill}), {swing} 스윙, {profile.driver_distance}야드 기준"
    if miss:
        context += f", {miss} 미스 교정 고려"
    return f"{context}. {base}"


# ── 페어웨이 우드 ─────────────────────────────────────────────────

_WOOD_REASON = {
    "페어웨이 우드":  "넓은 솔과 높은 MOI로 탑핑·뒤땅 모두 대응합니다. 페어웨이와 러프에서 안정적인 볼 스트라이킹이 가능합니다.",
    "로우스핀 우드":  "낮은 스핀으로 런 거리를 늘립니다. 풍속 영향을 줄이고 거리 극대화가 필요한 플레이어에게 적합합니다.",
    "고탄도 우드":    "높은 런치각으로 캐리 거리를 늘립니다. 스윙 속도가 느리거나 탄도가 낮아 거리 손실이 있는 경우에 유리합니다.",
}

def build_wood_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill = _skill_label(profile.handicap)
    miss  = FAIRWAY_MISS_KO.get(profile.fairway_miss)
    traj  = TRAJ_KO.get(profile.trajectory, "")
    base  = _WOOD_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = f"핸디캡 {profile.handicap}({skill}), 우드 {profile.wood_distance}야드, {traj} 탄도 선호"
    if miss:
        context += f", {miss} 미스 교정 고려"
    return f"{context}. {base}"


# ── 유틸리티 ─────────────────────────────────────────────────────

_UTILITY_REASON = {
    "하이브리드":    "롱아이언 대비 훨씬 높은 관용성과 탄도를 제공합니다. 3·4번 아이언을 대체하는 가장 대중적인 선택입니다.",
    "로우스핀 유틸": "낮은 탄도로 강한 침투력 구질을 만듭니다. 롱아이언 숙련자가 거리와 제어를 모두 원할 때 적합합니다.",
    "고탄도 유틸":   "높은 런치각으로 소프트한 착지를 도와줍니다. 타이트한 핀 공략이나 오르막 홀에서 유리합니다.",
}

def build_utility_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill      = _skill_label(profile.handicap)
    difficulty = LONG_IRON_KO.get(profile.long_iron_difficulty, "")
    traj       = TRAJ_KO.get(profile.trajectory, "")
    base       = _UTILITY_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = (f"핸디캡 {profile.handicap}({skill}), 롱아이언 난이도 '{difficulty}', "
               f"{traj} 탄도, 유틸 {profile.utility_distance}야드")
    return f"{context}. {base}"


# ── 아이언 ───────────────────────────────────────────────────────

_IRON_REASON = {
    "아이언 세트":              "캐비티백 설계로 스윗스팟이 넓고 관용성이 높습니다. 비거리와 방향성 모두 안정적인 결과를 원하는 아마추어에게 적합합니다.",
    "포지드 아이언":            "연단조 헤드로 타구감이 뛰어납니다. 정확한 임팩트와 일관된 볼 스트라이킹이 가능한 상급자를 위한 선택입니다.",
    "게임 임프루브먼트 아이언": "두꺼운 탑라인과 넓은 솔이 탑핑·뒤땅을 줄여줍니다. 실수가 잦고 비거리가 부족한 입문~중급자에게 최적입니다.",
}

def build_iron_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill = _skill_label(profile.handicap)
    miss  = IRON_MISS_KO.get(profile.miss_shot)
    traj  = TRAJ_KO.get(profile.trajectory, "")
    base  = _IRON_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = f"핸디캡 {profile.handicap}({skill}), 7번 아이언 {profile.iron_7_distance}야드, {traj} 탄도"
    if miss:
        context += f", {miss} 미스 교정 고려"
    return f"{context}. {base}"


# ── 웨지 ─────────────────────────────────────────────────────────

_WEDGE_REASON = {
    "웨지":      "범용성 높은 어프로치·벙커 웨지입니다. 다양한 라이에서 일관된 스핀과 거리 컨트롤을 제공합니다.",
    "로브 웨지": "높은 로프트로 급격한 탄도와 강한 스핀을 만듭니다. 짧은 어프로치, 벙커, 러프에서 빠른 정지가 필요할 때 강력합니다.",
    "갭 웨지":   "PW와 56도 사이 거리 공백을 채웁니다. 50~90야드 중거리 어프로치에서 거리 조절이 가장 쉬운 웨지입니다.",
}

def build_wedge_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill = _skill_label(profile.handicap)
    miss  = WEDGE_MISS_KO.get(profile.wedge_miss)
    spin  = SPIN_KO.get(profile.spin_need, "")
    base  = _WEDGE_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = f"핸디캡 {profile.handicap}({skill}), 어프로치 {profile.approach_distance}야드, {spin} 필요"
    if miss:
        context += f", {miss} 미스 교정 고려"
    return f"{context}. {base}"


# ── 퍼터 ─────────────────────────────────────────────────────────

_PUTTER_REASON = {
    "퍼터":      "범용적인 퍼터로 아크·직선 스트로크 모두 대응합니다. 방향성 문제와 거리감 모두 잡을 수 있는 기본형입니다.",
    "말렛 퍼터": "넓은 헤드와 높은 MOI로 직선 스트로크에 최적화됩니다. 방향 실수가 잦거나 거리 조절이 어려운 경우 유리합니다.",
    "블레이드 퍼터": "작은 헤드로 타구감과 거리감이 뛰어납니다. 일관된 스트로크와 높은 감각이 있는 상급자용 퍼터입니다.",
}

def build_putter_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    skill  = _skill_label(profile.handicap)
    miss   = PUTTING_MISS_KO.get(profile.putting_miss)
    dist   = DIST_CTRL_KO.get(profile.distance_control, "")
    stroke = STROKE_KO.get(profile.stroke_type, "")
    base   = _PUTTER_REASON.get(category_name, f"'{category_name}'을(를) 추천합니다.")

    context = f"핸디캡 {profile.handicap}({skill}), {stroke} 스트로크, 거리감 '{dist}'"
    if miss:
        context += f", {miss} 방향 미스 고려"
    return f"{context}. {base}"


# ── 디스패처 ─────────────────────────────────────────────────────

_BUILDERS = {
    "driver":  build_driver_reason,
    "wood":    build_wood_reason,
    "utility": build_utility_reason,
    "iron":    build_iron_reason,
    "wedge":   build_wedge_reason,
    "putter":  build_putter_reason,
}

def build_reason(profile, category_name: str, matched_traits: list[str]) -> str:
    fn = _BUILDERS.get(profile.club_type)
    if fn:
        return fn(profile, category_name, matched_traits)
    return f"'{category_name}'을(를) 추천합니다."
