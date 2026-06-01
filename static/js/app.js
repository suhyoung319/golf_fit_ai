"use strict";

// ── 상수 ──────────────────────────────────────────────────────────
const CLUB_TYPE_KO = {
  driver:"드라이버", wood:"페어웨이 우드", utility:"유틸리티",
  iron:"아이언", wedge:"웨지", putter:"퍼터",
};
const SHAFT_KO = {
  regular:"레귤러", stiff:"스티프", senior:"시니어",
  extra_stiff:"엑스트라 스티프", ladies:"레이디스",
};
const SKILL_KO = { beginner:"입문자", intermediate:"중급자", advanced:"상급자" };
const ENDPOINTS = {
  driver:"/api/recommend/driver", wood:"/api/recommend/wood",
  utility:"/api/recommend/utility", iron:"/api/recommend/iron",
  wedge:"/api/recommend/wedge", putter:"/api/recommend/putter",
};
const REQUIRED_NUMBER = {
  driver:"driver_distance", wood:"wood_distance", utility:"utility_distance",
  iron:"iron_7_distance", wedge:"approach_distance", putter:null,
};

function calcSkillLabel(h) {
  if (h === "" || isNaN(Number(h))) return "";
  const n = Number(h);
  if (n >= 25) return "🟢 입문자 (Beginner)";
  if (n >= 10) return "🟡 중급자 (Intermediate)";
  return "🔴 상급자 (Advanced)";
}

// ── DOM ────────────────────────────────────────────────────────────
const clubTypeBtns   = document.querySelectorAll(".club-type-btn");
const clubTypeInput  = document.getElementById("club_type");
const clubTypeError  = document.getElementById("club-type-error");
const dynamicArea    = document.getElementById("dynamic-form-area");
const handicapInput  = document.getElementById("handicap");
const skillAutoLabel = document.getElementById("skill-auto-label");
const form           = document.getElementById("recommend-form");
const submitBtn      = document.getElementById("submit-btn");
const submitLabel    = document.getElementById("submit-label");
const spinner        = document.getElementById("spinner");
const errorBox       = document.getElementById("error-box");
const resultSection  = document.getElementById("result-section");
const resClubType    = document.getElementById("res-club-type");
const resHandicap    = document.getElementById("res-handicap");
const resSkill       = document.getElementById("res-skill");
const mlResultCard   = document.getElementById("ml-result-card");
const top3List       = document.getElementById("top3-list");

// ── 클럽 타입 선택 ─────────────────────────────────────────────────
clubTypeBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    const val = btn.dataset.value;
    clubTypeBtns.forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    clubTypeInput.value = val;
    clubTypeError.classList.remove("visible");
    document.querySelectorAll(".sub-form").forEach(f => f.classList.remove("active"));
    const target = document.getElementById(`form-${val}`);
    if (target) target.classList.add("active");
    dynamicArea.style.display = "block";
    dynamicArea.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
});

// ── 핸디캡 → 실력 자동 표시 ──────────────────────────────────────
handicapInput.addEventListener("input", () => {
  skillAutoLabel.textContent = calcSkillLabel(handicapInput.value);
});

// ── 유틸 ──────────────────────────────────────────────────────────
function setLoading(on) {
  submitBtn.disabled        = on;
  submitLabel.style.display = on ? "none" : "inline";
  spinner.style.display     = on ? "block" : "none";
}
function showError(msg) { errorBox.textContent = msg; errorBox.style.display = "block"; }
function hideError()    { errorBox.style.display = "none"; }

function collectPayload(clubType) {
  const sub  = document.getElementById(`form-${clubType}`);
  const data = { club_type: clubType, handicap: Number(handicapInput.value) };
  sub.querySelectorAll("input[type='number'], select").forEach(el => {
    if (!el.name) return;
    data[el.name] = el.tagName === "SELECT" ? el.value : Number(el.value);
  });
  return data;
}

function formatWon(value) {
  return `${new Intl.NumberFormat("ko-KR").format(value)}원`;
}

function renderPriceRows(prices) {
  if (!prices?.length) {
    return `<div class="price-empty">등록된 판매처가 없습니다.</div>`;
  }

  return prices.map((p, index) => `
    <div class="price-row ${index === 0 ? "lowest" : ""}">
      <div class="price-info">
        <div class="price-seller">
          ${p.seller_name}
          ${index === 0 ? `<span class="lowest-badge">최저가</span>` : ""}
        </div>
        <div class="price-product">${p.product_name}</div>
      </div>
      <div class="price-actions">
        <div class="price-value">${formatWon(p.price)}</div>
        <a class="price-link" href="${p.product_url}" target="_blank" rel="noopener">구매</a>
      </div>
    </div>
  `).join("");
}

// ── Top3 카드 렌더링 ───────────────────────────────────────────────
function renderClubs(clubs) {
  if (!clubs?.length) return `<p style="font-size:13px;color:var(--gray-600)">클럽 데이터 없음</p>`;
  return clubs.map((c, i) => {
    const shaft = SHAFT_KO[c.shaft_type] ?? c.shaft_type;
    const flex  = c.flex ? `<span class="tag">플렉스 ${c.flex}</span>` : "";
    const loft  = c.loft_angle  ? `<span class="tag tag-loft">로프트 ${c.loft_angle}</span>` : "";
    const price = c.price_range ? `<span class="tag tag-price">💰 ${c.price_range}</span>` : "";
    const desc  = c.description ? `<p class="club-desc">${c.description}</p>` : "";
    const launch = c.launch_type ? `<span class="tag">탄도 ${c.launch_type}</span>` : "";
    const scores = `
      <div class="club-specs">
        <span>관용 ${c.forgiveness_score}</span>
        <span>거리 ${c.distance_score}</span>
        <span>컨트롤 ${c.control_score}</span>
        <span>스핀 ${c.spin_score}</span>
      </div>`;
    const pricesId = `prices-${c.id}`;
    return `
      <div class="club-card">
        <div class="club-header">
          <span class="club-num">${i+1}.</span>
          <div>
            <div class="club-brand">${c.brand}</div>
            <div class="club-model">${c.model_name}</div>
          </div>
        </div>
        ${desc}
        ${scores}
        <div class="club-meta">
          <span class="tag tag-shaft">샤프트 ${shaft}</span>${flex}${loft}${launch}${price}
        </div>
        <button class="price-toggle" type="button" onclick="togglePrices(${c.id}, '${pricesId}', this)">
          최저가 보기
        </button>
        <div class="price-list" id="${pricesId}"></div>
      </div>`;
  }).join("");
}

function renderTraits(traits) {
  if (!traits?.length) return "";
  return `<div class="traits-wrap">
    ${traits.map(t => `<span class="trait-tag">✓ ${t}</span>`).join("")}
  </div>`;
}

function renderRankCard(item) {
  const scoreWidth = `${item.score}%`;
  const clubsId    = `clubs-${item.rank}`;
  const listId     = `clubs-list-${item.rank}`;

  return `
    <div class="rank-card rank-${item.rank}">
      <div class="rank-header">
        <div class="rank-badge">${item.rank === 1 ? "🥇" : item.rank === 2 ? "🥈" : "🥉"}</div>
        <div class="rank-title-group">
          <div class="rank-category">${item.category_name}</div>
          <div class="rank-sub">추천 점수</div>
        </div>
        <div class="score-wrap">
          <div class="score-number">${item.score}</div>
          <div class="score-bar-track">
            <div class="score-bar-fill" style="width:${scoreWidth}"></div>
          </div>
        </div>
      </div>
      <div class="rank-body">
        <div class="reason-text">${item.reason}</div>
        ${renderTraits(item.matched_traits)}
        <button class="clubs-toggle" id="${clubsId}"
                onclick="toggleClubs('${clubsId}','${listId}')">
          추천 클럽 ${item.clubs.length}개 보기
          <i class="arrow">▾</i>
        </button>
        <div class="clubs-list" id="${listId}">
          ${renderClubs(item.clubs)}
        </div>
      </div>
    </div>`;
}

function renderMlResult(data) {
  if (!mlResultCard) return;

  if (!data.ml_prediction) {
    mlResultCard.className = "ml-result-card unavailable";
    mlResultCard.innerHTML = `
      <div class="ml-title-row">
        <h3>ML 기반 예측 결과</h3>
      </div>
      <p class="ml-empty">ML 모델을 불러오지 못해 Rule 기반 추천만 표시됩니다.</p>
    `;
    return;
  }

  const confidence = data.ml_prediction.confidence;
  const confidenceText = typeof confidence === "number"
    ? `${(confidence * 100).toFixed(1)}%`
    : "-";
  const agreementText = data.ml_agreement
    ? "Rule 1순위와 일치"
    : "Rule 1순위와 불일치";
  const agreementClass = data.ml_agreement ? "agree" : "disagree";

  mlResultCard.className = `ml-result-card ${agreementClass}`;
  mlResultCard.innerHTML = `
    <div class="ml-title-row">
      <h3>ML 기반 예측 결과</h3>
      <span class="ml-agreement ${agreementClass}">${agreementText}</span>
    </div>
    <div class="ml-grid">
      <div class="ml-metric">
        <span class="ml-label">예측 카테고리</span>
        <strong>${data.ml_prediction.category_name}</strong>
      </div>
      <div class="ml-metric">
        <span class="ml-label">예측 신뢰도</span>
        <strong>${confidenceText}</strong>
      </div>
      <div class="ml-metric">
        <span class="ml-label">Rule 1순위</span>
        <strong>${data.rule_top1 ?? "-"}</strong>
      </div>
    </div>
  `;
}

function toggleClubs(btnId, listId) {
  const btn  = document.getElementById(btnId);
  const list = document.getElementById(listId);
  const open = list.classList.toggle("open");
  btn.classList.toggle("open", open);
  btn.querySelector("i").textContent = open ? "▴" : "▾";
}
window.toggleClubs = toggleClubs;

async function togglePrices(clubId, listId, btn) {
  const list = document.getElementById(listId);
  if (!list) return;

  if (list.classList.contains("open")) {
    list.classList.remove("open");
    btn.textContent = "최저가 보기";
    return;
  }

  list.classList.add("open");
  btn.textContent = "가격 접기";

  if (list.dataset.loaded === "true") return;

  list.innerHTML = `<div class="price-loading">가격 정보를 불러오는 중...</div>`;
  try {
    const resp = await fetch(`/api/clubs/${clubId}/prices`);
    if (!resp.ok) {
      list.innerHTML = `<div class="price-empty">가격 정보를 불러오지 못했습니다.</div>`;
      return;
    }
    const prices = await resp.json();
    list.innerHTML = renderPriceRows(prices);
    list.dataset.loaded = "true";
  } catch (err) {
    list.innerHTML = `<div class="price-empty">네트워크 오류: ${err.message}</div>`;
  }
}
window.togglePrices = togglePrices;

// ── 결과 렌더링 ────────────────────────────────────────────────────
function renderResult(data) {
  resClubType.textContent = CLUB_TYPE_KO[data.club_type] ?? data.club_type;
  resHandicap.textContent = data.handicap;
  const skillLabel = SKILL_KO[data.calculated_skill] ?? data.calculated_skill;
  resSkill.innerHTML =
    `<span class="skill-badge ${data.calculated_skill}">${skillLabel}</span>`;
  renderMlResult(data);

  if (!data.recommendations?.length) {
    top3List.innerHTML = `<div class="empty-state">추천 결과가 없습니다.<br>seed_data.py 실행 여부를 확인하세요.</div>`;
  } else {
    top3List.innerHTML = data.recommendations.map(renderRankCard).join("");
    // 1위 클럽 자동 열기
    const firstList = document.getElementById("clubs-list-1");
    const firstBtn  = document.getElementById("clubs-1");
    if (firstList && firstBtn) {
      firstList.classList.add("open");
      firstBtn.classList.add("open");
      firstBtn.querySelector("i").textContent = "▴";
    }
  }

  resultSection.style.display = "block";
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── 폼 제출 ────────────────────────────────────────────────────────
form.addEventListener("submit", async e => {
  e.preventDefault();
  hideError();

  const clubType = clubTypeInput.value;
  if (!clubType) {
    clubTypeError.classList.add("visible");
    document.getElementById("club-type-grid").scrollIntoView({ behavior: "smooth" });
    return;
  }

  const hcp = Number(handicapInput.value);
  if (isNaN(hcp) || hcp < 0 || hcp > 54) {
    showError("핸디캡은 0~54 사이로 입력해주세요.");
    return;
  }

  const reqField = REQUIRED_NUMBER[clubType];
  if (reqField) {
    const el = document.getElementById(`form-${clubType}`)?.querySelector(`[name="${reqField}"]`);
    if (!el?.value) { showError("비거리 / 거리 항목을 입력해주세요."); return; }
  }

  setLoading(true);
  try {
    const resp = await fetch(ENDPOINTS[clubType], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectPayload(clubType)),
    });

    if (!resp.ok) {
      const err = await resp.json();
      if (resp.status === 422 && Array.isArray(err.detail))
        showError("입력값 오류: " + err.detail.map(d => d.msg).join(" / "));
      else
        showError(`서버 오류 (${resp.status}): ${JSON.stringify(err.detail ?? err)}`);
      return;
    }
    renderResult(await resp.json());
  } catch (err) {
    showError(`네트워크 오류: ${err.message}`);
  } finally {
    setLoading(false);
  }
});
