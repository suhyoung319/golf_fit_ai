from app.schemas.user_input import GolfProfileInput

# handicap → 내부 실력 레이블 (reason 텍스트용)
def _skill_label(handicap: int) -> str:
    if handicap >= 25:
        return "입문자"
    if handicap >= 10:
        return "중급자"
    return "상급자"

MISS_KO = {
    "slice":  "슬라이스",
    "hook":   "훅",
    "top":    "탑핑",
    "fat":    "뒤땅",
    "push":   "푸시",
    "pull":   "풀",
    "none":   None,
}

SWING_KO = {
    "slow":   "느린",
    "medium": "보통",
    "fast":   "빠른",
}

CLUB_TYPE_KO = {
    "driver":  "드라이버",
    "wood":    "페어웨이 우드",
    "utility": "유틸리티",
    "iron":    "아이언",
    "wedge":   "웨지",
    "putter":  "퍼터",
}


def build_reason(profile: GolfProfileInput, category_name: str) -> str:
    """
    추천 이유 텍스트 생성.
    추후 LLM 기반으로 교체할 경우 이 함수만 수정하면 됨.
    """
    skill   = _skill_label(profile.handicap)
    miss    = MISS_KO.get(profile.miss_shot_type)
    swing   = SWING_KO.get(profile.swing_speed, profile.swing_speed)
    club_ko = CLUB_TYPE_KO.get(profile.club_type, profile.club_type)

    parts = [
        f"핸디캡 {profile.handicap}({skill}) 기준,"
        f" {swing} 스윙 속도에 평균 비거리 {profile.distance_avg}야드를 고려했을 때"
    ]

    if miss:
        parts.append(f"{miss} 미스샷 교정에 유리한")

    parts.append(f"{club_ko} 중 '{category_name}'을(를) 추천합니다.")

    return " ".join(parts)
