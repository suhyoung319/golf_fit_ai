"use strict";

// ── 상수 ──────────────────────────────────────────────────────
const SHAFT_KO = {
  regular:     "레귤러",
  stiff:       "스티프",
  senior:      "시니어",
  extra_stiff: "엑스트라 스티프",
  ladies:      "레이디스",
};

const CLUB_TYPE_KO = {
  driver:  "드라이버",
  wood:    "페어웨이 우드",
  utility: "유틸리티",
  iron:    "아이언",
  wedge:   "웨지",
  putter:  "퍼터",
};

// handicap → 실력 레이블 (폼 안내용, 서버와 동일 기준)
function calcSkillLabel(handicap) {
  if (handicap === "" || isNaN(handicap)) return "";
  const h = Number(handicap);
  if (h >= 25) return "🟢 입문자 (Beginner)";
  if (h >= 10) return "🟡 중급자 (Intermediate)";
  return "🔴 상급자 (Advanced)";
}

// ── DOM 참조 ───────────────────────────────────────────────────
const form           = document.getElementById("recommend-form");
const clubTypeBtns   = document.querySelectorAll(".club-type-btn");
const clubTypeInput  = document.getElementById("club_type");
const clubTypeError  = document.getElementById("club-type-error");
const handicapInput  = document.getElementById("handicap");
const skillAutoLabel = document.getElementById("skill-auto-label");
const submitBtn      = document.getElementById("submit-btn");
const submitLabel    = document.getElementById("submit-label");
const spinner        = document.getElementById("spinner");
const errorBox       = document.getElementById("error-box");

const resultSection  = document.getElementById("result-section");
const resultClubType = document.getElementById("result-club-type");
const resultCategory = document.getElementById("result-category");
const reasonText     = document.getElementById("reason-text");
const clubList       = document.getElementById("club-list");


// ── 클럽 타입 버튼 선택 ────────────────────────────────────────
clubTypeBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    clubTypeBtns.forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    clubTypeInput.value = btn.dataset.value;
    clubTypeError.classList.remove("visible");
  });
});

// ── 핸디캡 입력 → 실력 자동 표시 ──────────────────────────────
handicapInput.addEventListener("input", () => {
  skillAutoLabel.textContent = calcSkillLabel(handicapInput.value);
});


// ── 유틸 ──────────────────────────────────────────────────────
function setLoading(on) {
  submitBtn.disabled        = on;
  submitLabel.style.display = on ? "none"  : "inline";
  spinner.style.display     = on ? "block" : "none";
}

function showError(msg) {
  errorBox.textContent   = msg;
  errorBox.style.display = "block";
}

function hideError() {
  errorBox.style.display = "none";
}


// ── 클럽 카드 HTML 생성 ────────────────────────────────────────
function renderClubCard(club, index) {
  const shaft = SHAFT_KO[club.shaft_type] ?? club.shaft_type;
  const loft  = club.loft_angle
    ? `<span class="tag tag-loft">로프트 ${club.loft_angle}</span>` : "";
  const price = club.price_range
    ? `<span class="tag tag-price">💰 ${club.price_range}</span>` : "";
  const desc  = club.description
    ? `<p class="club-desc">${club.description}</p>` : "";

  return `
    <div class="club-card">
      <div class="club-header">
        <div class="club-rank">${index + 1}</div>
        <div>
          <div class="club-brand">${club.brand}</div>
          <div class="club-model">${club.model_name}</div>
        </div>
      </div>
      ${desc}
      <div class="club-meta">
        <span class="tag tag-shaft">샤프트 ${shaft}</span>
        ${loft}
        ${price}
      </div>
    </div>`;
}


// ── 결과 렌더링 ────────────────────────────────────────────────
function renderResult(data) {
  // 선택 클럽 종류 → 추천 카테고리
  resultClubType.textContent = CLUB_TYPE_KO[data.club_type] ?? data.club_type;
  resultCategory.textContent = data.category_name;
  reasonText.textContent     = data.reason;

  if (!data.clubs || data.clubs.length === 0) {
    clubList.innerHTML =
      `<div class="empty-state">추천 클럽 데이터가 없습니다.<br>seed_data.py 실행 여부를 확인하세요.</div>`;
  } else {
    clubList.innerHTML = data.clubs.map(renderClubCard).join("");
  }

  resultSection.style.display = "block";
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ── 폼 제출 ───────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();

  // 클럽 타입 선택 검증
  if (!clubTypeInput.value) {
    clubTypeError.classList.add("visible");
    document.getElementById("club-type-grid").scrollIntoView({ behavior: "smooth" });
    return;
  }

  setLoading(true);

  const payload = {
    club_type:      clubTypeInput.value,
    miss_shot_type: form.miss_shot_type.value,
    distance_avg:   Number(form.distance_avg.value),
    handicap:       Number(form.handicap.value),
    swing_speed:    form.swing_speed.value,
  };

  try {
    const resp = await fetch("/api/recommend", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await resp.json();
      if (resp.status === 422 && Array.isArray(err.detail)) {
        const msgs = err.detail.map(d => d.msg).join(" / ");
        showError(`입력값 오류: ${msgs}`);
      } else {
        showError(`서버 오류 (${resp.status}): ${JSON.stringify(err.detail ?? err)}`);
      }
      return;
    }

    const data = await resp.json();
    renderResult(data);

  } catch (err) {
    showError(`네트워크 오류: ${err.message}`);
  } finally {
    setLoading(false);
  }
});
