"""
룰 기반 가중치 점수 산출 엔진.

설계 원칙:
- 각 club_type별로 독립적인 trait 체크 함수를 가짐
- 각 trait는 (조건 충족 여부, trait_label, 점수) 튜플을 반환
- 추후 ML 모델로 교체 시 이 파일만 교체하면 됨
- 학습 데이터 수집: 사용자 입력 + matched_traits + score가 자연스럽게 피처/레이블이 됨

점수 구조:
- 각 카테고리는 해당 상황에 얼마나 잘 맞는지를 0~100으로 표현
- 기준 점수(base) 50 + trait 가중치 합산
- 최대 100점 clamp
"""
from dataclasses import dataclass


@dataclass
class TraitResult:
    matched: bool
    label: str       # matched_traits에 노출되는 영문 레이블
    score: int       # 이 trait가 매칭됐을 때 더하는 점수


def _clamp(v: int) -> int:
    return max(0, min(100, v))


# ── 드라이버 ─────────────────────────────────────────────────────

def score_driver(profile, category_name: str) -> tuple[int, list[str]]:
    """
    드라이버 카테고리별 점수 산출.
    카테고리명에 따라 가중치 기준이 달라짐.
    """
    p = profile
    base = 50

    # trait 목록 정의
    traits: list[TraitResult] = []

    if category_name == "고반발 드라이버":
        traits = [
            TraitResult(p.miss_shot == "slice",        "slice correction",        15),
            TraitResult(p.miss_shot == "hook",         "hook correction",         12),
            TraitResult(p.swing_speed == "slow",       "slow swing speed",        10),
            TraitResult(p.driver_distance < 180,       "short distance support",  10),
            TraitResult(p.handicap >= 25,              "beginner friendly",        8),
            TraitResult(p.miss_shot in ("high","low"), "trajectory instability",   5),
        ]
    elif category_name == "슬라이스 보정 드라이버":
        traits = [
            TraitResult(p.miss_shot == "slice",        "slice correction",        20),
            TraitResult(p.swing_speed == "slow",       "slow swing speed",         8),
            TraitResult(p.handicap >= 20,              "high handicap",           10),
            TraitResult(p.driver_distance < 200,       "short distance support",   7),
            TraitResult(p.miss_shot == "push",         "push correction",          5),
        ]
    elif category_name == "드라이버":
        traits = [
            TraitResult(p.handicap < 25,               "intermediate+ skill",     12),
            TraitResult(p.swing_speed == "medium",     "medium swing speed",      10),
            TraitResult(p.swing_speed == "fast",       "fast swing speed",         8),
            TraitResult(p.driver_distance >= 200,      "adequate distance",        10),
            TraitResult(p.miss_shot == "none",         "consistent ball flight",   8),
            TraitResult(p.miss_shot == "hook",         "hook correction",          6),
        ]
    elif category_name == "투어 드라이버":
        traits = [
            TraitResult(p.handicap < 10,               "advanced skill",          20),
            TraitResult(p.swing_speed == "fast",       "fast swing speed",        15),
            TraitResult(p.driver_distance >= 250,      "long distance",           10),
            TraitResult(p.miss_shot == "none",         "shot consistency",        10),
            TraitResult(p.miss_shot == "low",          "low trajectory control",   5),
        ]
    else:
        # 알 수 없는 카테고리 — 기본 점수만
        return base, []

    matched = [t.label for t in traits if t.matched]
    total   = base + sum(t.score for t in traits if t.matched)
    return _clamp(total), matched


# ── 페어웨이 우드 ─────────────────────────────────────────────────

def score_wood(profile, category_name: str) -> tuple[int, list[str]]:
    p = profile
    base = 50
    traits: list[TraitResult] = []

    if category_name == "페어웨이 우드":
        traits = [  
            TraitResult(p.fairway_miss == "thin",      "thin shot correction",    12),
            TraitResult(p.fairway_miss == "fat",       "fat shot correction",     10),
            TraitResult(p.trajectory == "high",        "high trajectory need",     8),
            TraitResult(p.trajectory == "mid",         "balanced trajectory",      6),
            TraitResult(p.wood_distance < 220,         "distance support",         8),
            TraitResult(p.handicap >= 15,              "forgiveness priority",     6),
        ]
    elif category_name == "로우스핀 우드":
        traits = [
            TraitResult(p.trajectory == "low",         "low trajectory",          15),
            TraitResult(p.wood_distance >= 220,        "long distance",           10),
            TraitResult(p.handicap < 15,               "skilled player",          10),
            TraitResult(p.fairway_miss == "none",      "consistent contact",       8),
        ]
    elif category_name == "고탄도 우드":
        traits = [
            TraitResult(p.trajectory == "high",        "high launch need",        18),
            TraitResult(p.wood_distance < 200,         "carry distance support",  10),
            TraitResult(p.handicap >= 20,              "beginner friendly",        8),
            TraitResult(p.fairway_miss in ("thin","fat"), "mis-hit forgiveness",   6),
        ]
    else:
        return base, []

    matched = [t.label for t in traits if t.matched]
    return _clamp(base + sum(t.score for t in traits if t.matched)), matched


# ── 유틸리티 ─────────────────────────────────────────────────────

def score_utility(profile, category_name: str) -> tuple[int, list[str]]:
    p = profile
    base = 50
    traits: list[TraitResult] = []

    if category_name == "하이브리드":
        traits = [
            TraitResult(p.long_iron_difficulty == "very_hard", "long iron difficulty",   18),
            TraitResult(p.long_iron_difficulty == "hard",      "long iron challenge",    12),
            TraitResult(p.trajectory == "high",                "high trajectory need",    8),
            TraitResult(p.handicap >= 20,                      "beginner friendly",       8),
            TraitResult(p.utility_distance < 200,              "distance support",        6),
        ]
    elif category_name == "로우스핀 유틸":
        traits = [
            TraitResult(p.trajectory == "low",                 "low ball flight",        15),
            TraitResult(p.handicap < 15,                       "skilled player",         12),
            TraitResult(p.utility_distance >= 200,             "long utility distance",  10),
            TraitResult(p.long_iron_difficulty == "ok",        "iron proficient",         8),
        ]
    elif category_name == "고탄도 유틸":
        traits = [
            TraitResult(p.trajectory == "high",                "high launch need",       18),
            TraitResult(p.long_iron_difficulty != "ok",        "iron replacement need",  10),
            TraitResult(p.handicap >= 15,                      "forgiveness priority",    8),
        ]
    else:
        return base, []

    matched = [t.label for t in traits if t.matched]
    return _clamp(base + sum(t.score for t in traits if t.matched)), matched


# ── 아이언 ───────────────────────────────────────────────────────

def score_iron(profile, category_name: str) -> tuple[int, list[str]]:
    p = profile
    base = 50
    traits: list[TraitResult] = []

    if category_name == "아이언 세트":
        traits = [
            TraitResult(p.miss_shot == "duff",         "duff correction",         14),
            TraitResult(p.miss_shot == "top",          "top correction",          12),
            TraitResult(p.trajectory == "high",        "high trajectory need",     8),
            TraitResult(p.iron_7_distance < 150,       "distance support",         8),
            TraitResult(p.handicap >= 18,              "forgiveness priority",    10),
        ]
    elif category_name == "포지드 아이언":
        traits = [
            TraitResult(p.handicap < 10,               "advanced skill",          20),
            TraitResult(p.miss_shot == "none",         "shot consistency",        12),
            TraitResult(p.iron_7_distance >= 160,      "strong iron distance",    10),
            TraitResult(p.trajectory == "low",         "low trajectory control",   8),
            TraitResult(p.miss_shot == "pull",         "pull correction",          5),
        ]
    elif category_name == "게임 임프루브먼트 아이언":
        traits = [
            TraitResult(p.handicap >= 15,              "high handicap",           14),
            TraitResult(p.miss_shot in ("duff","top"), "contact instability",     12),
            TraitResult(p.iron_7_distance < 160,       "distance need",           10),
            TraitResult(p.trajectory == "mid",         "mid trajectory",           6),
        ]
    else:
        return base, []

    matched = [t.label for t in traits if t.matched]
    return _clamp(base + sum(t.score for t in traits if t.matched)), matched


# ── 웨지 ─────────────────────────────────────────────────────────

def score_wedge(profile, category_name: str) -> tuple[int, list[str]]:
    p = profile
    base = 50
    traits: list[TraitResult] = []

    if category_name == "웨지":
        traits = [
            TraitResult(p.spin_need == "high",         "high spin need",          14),
            TraitResult(p.wedge_miss == "chunk",       "chunk correction",        12),
            TraitResult(p.wedge_miss == "skull",       "skull correction",        10),
            TraitResult(p.approach_distance <= 100,    "short game focus",         8),
            TraitResult(p.handicap >= 10,              "versatile selection",      6),
        ]
    elif category_name == "로브 웨지":
        traits = [
            TraitResult(p.spin_need == "high",         "high spin need",          18),
            TraitResult(p.approach_distance <= 60,     "short approach",          14),
            TraitResult(p.handicap < 15,               "skilled player",          10),
            TraitResult(p.wedge_miss == "short",       "short miss correction",    6),
        ]
    elif category_name == "갭 웨지":
        traits = [
            TraitResult(p.approach_distance >= 80,     "mid-range approach",      14),
            TraitResult(p.spin_need == "medium",       "medium spin",             10),
            TraitResult(p.wedge_miss == "long",        "long miss correction",    10),
            TraitResult(p.handicap >= 10,              "versatile use",            6),
        ]
    else:
        return base, []

    matched = [t.label for t in traits if t.matched]
    return _clamp(base + sum(t.score for t in traits if t.matched)), matched


# ── 퍼터 ─────────────────────────────────────────────────────────

def score_putter(profile, category_name: str) -> tuple[int, list[str]]:
    p = profile
    base = 50
    traits: list[TraitResult] = []

    if category_name == "퍼터":
        traits = [
            TraitResult(p.putting_miss in ("left","right"), "directional miss",   12),
            TraitResult(p.stroke_type == "arc",            "arc stroke",          10),
            TraitResult(p.distance_control == "poor",      "distance control issue", 10),
            TraitResult(p.handicap >= 15,                  "high handicap",         8),
        ]
    elif category_name == "말렛 퍼터":
        traits = [
            TraitResult(p.stroke_type == "straight",       "straight stroke",     16),
            TraitResult(p.putting_miss in ("left","right"),"directional miss",    12),
            TraitResult(p.distance_control == "poor",      "distance issue",       8),
            TraitResult(p.handicap >= 15,                  "beginner friendly",    6),
        ]
    elif category_name == "블레이드 퍼터":
        traits = [
            TraitResult(p.handicap < 10,                   "advanced skill",      18),
            TraitResult(p.stroke_type == "arc",            "arc stroke",          12),
            TraitResult(p.distance_control == "good",      "good distance feel",  10),
            TraitResult(p.putting_miss == "none",          "consistent putting",   8),
        ]
    else:
        return base, []

    matched = [t.label for t in traits if t.matched]
    return _clamp(base + sum(t.score for t in traits if t.matched)), matched


# ── 디스패처 ─────────────────────────────────────────────────────

SCORERS = {
    "driver":  score_driver,
    "wood":    score_wood,
    "utility": score_utility,
    "iron":    score_iron,
    "wedge":   score_wedge,
    "putter":  score_putter,
}

def calc_score(profile, category_name: str) -> tuple[int, list[str]]:
    fn = SCORERS.get(profile.club_type)
    if fn:
        return fn(profile, category_name)
    return 50, []
