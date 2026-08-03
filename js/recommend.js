// 여행 추천 페이지 — 폼 제출 → /api/recommend 호출 → 결과 렌더링
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("recommendForm");
  const dateInput = document.getElementById("dateInput");
  const submitBtn = document.getElementById("submitBtn");
  const formMessage = document.getElementById("formMessage");
  const resultEl = document.getElementById("result");

  const FETCH_TIMEOUT_MS = 12000;

  function showFormMessage(text) {
    formMessage.textContent = text;
    formMessage.classList.add("visible");
  }

  function clearFormMessage() {
    formMessage.textContent = "";
    formMessage.classList.remove("visible");
  }

  function renderLoading() {
    resultEl.innerHTML = '<div class="loading">AI가 여행지를 찾고 있어요...</div>';
  }

  function renderError(message) {
    resultEl.innerHTML = `<p class="form-message visible">${message}</p>`;
  }

  function renderResult(data) {
    const events = (data.events || [])
      .map((e) => `<li>${e}</li>`)
      .join("");

    const restaurants = (data.restaurants || [])
      .map(
        (r) => `
        <div class="restaurant-card">
          <strong>${r.name}</strong>
          <div class="category">${r.category || ""}</div>
          <div>${r.address || ""}</div>
        </div>`
      )
      .join("");

    resultEl.innerHTML = `
      <div class="result-card">
        <h2>${data.recommended_city}</h2>
        <p>${data.reason || ""}</p>
        <p><strong>날씨</strong>: ${data.weather || "-"}</p>
        <ul class="tag-list">${events}</ul>
        <h3>주변 맛집</h3>
        <div class="restaurant-grid">
          ${restaurants || "<p>맛집 정보를 찾지 못했어요.</p>"}
        </div>
      </div>
    `;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormMessage();

    const date = dateInput.value;
    if (!date) {
      showFormMessage("여행 날짜를 선택해주세요.");
      return;
    }

    submitBtn.disabled = true;
    renderLoading();

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date }),
        signal: controller.signal,
      });

      if (!res.ok) {
        renderError("추천을 가져오는 데 실패했어요. 잠시 후 다시 시도해주세요.");
        return;
      }

      const data = await res.json();
      renderResult(data);
    } catch (err) {
      if (err.name === "AbortError") {
        renderError("응답이 지연되고 있어요. 잠시 후 다시 시도해주세요.");
      } else {
        renderError("추천을 가져오는 데 실패했어요. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      clearTimeout(timer);
      submitBtn.disabled = false;
    }
  });
});
