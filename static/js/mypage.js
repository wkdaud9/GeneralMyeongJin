document.addEventListener("DOMContentLoaded", () => {
  const moreHistoryBtn = document.getElementById("more-history-btn");
  const readHistoryList = document.getElementById("read-history-list");
  const wordHistoryList = document.getElementById("word-history-list");

  if (moreHistoryBtn) {
    moreHistoryBtn.addEventListener("click", async () => {
      moreHistoryBtn.disabled = true;
      moreHistoryBtn.textContent = "불러오는 중...";

      try {
        const [articlesResponse, wordsResponse] = await Promise.all([
          fetch("/mypage/api/history/articles"),
          fetch("/mypage/api/history/words"),
        ]);

        const articlesData = await articlesResponse.json();
        const wordsData = await wordsResponse.json();

        // --- 기사 기록 목록 업데이트 ---
        readHistoryList.innerHTML = "";
        if (articlesData.length > 0) {
          // ▼▼▼ 이 부분을 수정했습니다 ▼▼▼
          articlesData.forEach((article) => {
            const html = `
                            <a href="${article.url}" target="_blank" class="history-item">
                                <img src="${article.thumbnail}" class="history-thumb" alt="${article.title}">
                                <div class="history-item-content"><h4>${article.title}</h4></div>
                            </a>`;
            readHistoryList.insertAdjacentHTML("beforeend", html);
          });
        } else {
          readHistoryList.innerHTML =
            '<p class="empty-message">지난 7일간 읽은 기사가 없습니다.</p>';
        }

        // --- 단어 기록 목록 업데이트 (여기는 정상 동작) ---
        wordHistoryList.innerHTML = "";
        if (wordsData.length > 0) {
          wordsData.forEach((item) => {
            const html = `
                            <div class="history-item">
                                <div class="history-item-content">
                                    <h4>${item.word}</h4><p>${item.definition}</p>
                                </div>
                            </div>`;
            wordHistoryList.insertAdjacentHTML("beforeend", html);
          });
        } else {
          wordHistoryList.innerHTML =
            '<p class="empty-message">지난 7일간 찾아본 단어가 없습니다.</p>';
        }

        readHistoryList.classList.add("scrollable");
        wordHistoryList.classList.add("scrollable");
        moreHistoryBtn.style.display = "none";

        moreHistoryBtn.style.display = "none";
      } catch (error) {
        console.error("Error fetching history:", error);
        alert("기록을 불러오는 데 실패했습니다.");
        moreHistoryBtn.disabled = false;
        moreHistoryBtn.textContent = "지난 7일 기록 모두 보기";
      }
    });
  }
});
