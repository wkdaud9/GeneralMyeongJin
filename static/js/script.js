document.addEventListener("DOMContentLoaded", () => {
  // 1. 주요 HTML 요소들을 미리 찾아둡니다.
  const newsLayout = document.querySelector(".news-layout");
  const rankingList = document.querySelector(".ranking-list");
  const menuLinks = document.querySelectorAll(".category-link");
  const newsLayoutContainer = document.querySelector(".news-layout-container");
  const seeMoreBtn = document.getElementById("see-more-btn");
  const loaderOverlay = document.getElementById("loader-overlay");

  // 모달 관련 요소
  const choiceModal = document.querySelector(".news-modal");
  const modalTitle = document.getElementById("modal-title");
  const summarizeBtn = document.getElementById("summarize-btn");
  const originalLinkBtn = document.getElementById("original-link-btn");
  const choiceModalCloseBtn = document.querySelector(".modal-close-btn");

  // 리더 뷰(요약+사전) 모달 요소
  const readerView = document.getElementById("reader-view");
  const readerTitle = document.getElementById("reader-title");
  const readerContent = document.getElementById("reader-content");
  const dictionaryCurrent = document.getElementById("dictionary-current");
  const dictionaryHistory = document.getElementById("dictionary-history");
  const readerCloseBtn = document.getElementById("reader-close-btn");

  const sidebarTabs = document.querySelectorAll(".tab-link");
  const tabContents = document.querySelectorAll(".dictionary-pane .tab-content");

  let summaryPromise = null;
  let currentArticleId = null;

  // 2. 뉴스 데이터를 받아 화면에 그려주는 함수
  const renderNews = (newsData, rankingData) => {
    newsLayout.innerHTML = "";
    rankingList.innerHTML = "";
    if (!newsData || newsData.length === 0) {
      newsLayout.innerHTML = "<p>표시할 뉴스가 없습니다.</p>";
      return;
    }
    const featured = newsData[0];
    const featuredHtml = `
              <article class="news-item featured" data-article-id="${featured.article_id}" data-url="${featured.url}">
                  <img src="${featured.thumbnail}" alt="${featured.title}" class="image-placeholder">
                  <div class="article-content">
                      <h4>${featured.title}</h4>
                      </div>
              </article>`;
    newsLayout.insertAdjacentHTML("beforeend", featuredHtml);

    newsData.slice(1).forEach((news) => {
      const newsHtml = `
                          <article class="news-item" data-article-id="${news.article_id}" data-url="${news.url}">
                              <img src="${news.thumbnail}" alt="${news.title}" class="image-placeholder small">
                              <div class="article-content">
                                  <h5>${news.title}</h5>
                                  </div>
                          </article>`;
      newsLayout.insertAdjacentHTML("beforeend", newsHtml);
    });

    if (rankingData && rankingData.length > 0) {
      rankingData.forEach((news) => {
        const rankingHtml = `
                          <article class="ranking-item" data-article-id="${news.article_id}" data-url="${news.url}">
                              <img src="${news.thumbnail}" alt="${news.title}" class="image-placeholder rank">
                              <div class="article-content"><h6>${news.title}</h6></div>
                          </article>`;
        rankingList.insertAdjacentHTML("beforeend", rankingHtml);
      });
    } else {
      rankingList.innerHTML = "<p>랭킹 정보가 없습니다.</p>";
    }
    attachModalEvents();
  };

  // 3. 특정 카테고리의 뉴스를 API로 요청하는 함수
  const fetchAndRenderNews = async (category) => {
    newsLayoutContainer.classList.remove("expanded");
    seeMoreBtn.classList.remove("hidden");
    newsLayout.innerHTML = "<p>뉴스를 불러오는 중...</p>";
    rankingList.innerHTML = "<p>랭킹을 불러오는 중...</p>";
    try {
      const response = await fetch(`/api/articles/${category}`);
      const data = await response.json();
      renderNews(data.news_list, data.ranking_list);
    } catch (error) {
      console.error("뉴스 로딩 에러:", error);
      newsLayout.innerHTML = "<p>뉴스를 불러오는데 실패했습니다.</p>";
    }
  };

  // 4. 메뉴 링크에 클릭 이벤트 할당
  menuLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const category = e.target.dataset.category;
      menuLinks.forEach((l) => l.classList.remove("active"));
      e.target.classList.add("active");
      fetchAndRenderNews(category);
    });
  });

  // 5. '더보기' 버튼 클릭 이벤트
  seeMoreBtn.addEventListener("click", () => {
    newsLayoutContainer.classList.add("expanded");
    seeMoreBtn.classList.add("hidden");
  });

  // 6. 모달 관련 이벤트들을 할당하는 함수
  const attachModalEvents = () => {
    document
      .querySelectorAll(".news-item, .ranking-item")
      .forEach((article) => {
        article.style.cursor = "pointer";
        article.addEventListener("click", () => openChoiceModal(article));
      });
  };

  // 7. 뉴스 클릭 시 선택지 모달을 열고, 조회수를 올리는 함수
  const openChoiceModal = (articleElement) => {
    const title = articleElement.querySelector("h4, h5, h6").textContent;
    const url = articleElement.dataset.url;
    currentArticleId = articleElement.dataset.articleId;

    if (currentArticleId) {
      fetch(`/api/news/view/${currentArticleId}`, { method: "POST" }).catch(
        (error) => console.error("Failed to record view:", error)
      );
    }

    modalTitle.textContent = title;
    originalLinkBtn.href = url;

    summaryPromise = fetch("/api/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url }),
    });

    choiceModal.showModal();
  };

  // 8. 'AI로 풀어보기' 버튼 클릭 이벤트
  summarizeBtn.addEventListener("click", async () => {
    if (!summaryPromise) return;

    choiceModal.close();
    loaderOverlay.classList.remove("hidden");
    setTimeout(() => loaderOverlay.classList.add("visible"), 10);

    try {
      const response = await summaryPromise;
      if (!response.ok)
        throw new Error("요약 정보를 불러오는 데 실패했습니다.");
      const data = await response.json();

      readerTitle.textContent = modalTitle.textContent;
      readerContent.innerHTML = data.summary;

      dictionaryCurrent.innerHTML =
        '<p class="placeholder">궁금한 단어를 드래그 해보세요!</p>';
      dictionaryHistory.innerHTML = "";

      readerView.classList.remove("hidden");
      setTimeout(() => readerView.classList.add("visible"), 10);
    } catch (error) {
      alert(`AI 분석 실패: ${error.message}`);
    } finally {
      loaderOverlay.classList.remove("visible");
      setTimeout(() => loaderOverlay.classList.add("hidden"), 300);
    }
  });

  // 9. 단어 뜻 찾기(드래그) 이벤트
  readerContent.addEventListener("mouseup", async () => {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText.length > 0 && selectedText.length < 15) {
      
      const backgroundTab = document.querySelector('.tab-link[data-tab="tab-previous-articles"]');
      if (backgroundTab && backgroundTab.classList.contains("active")) {
        const backgroundContent = document.getElementById('tab-previous-articles');
        backgroundTab.classList.remove('active');
        backgroundContent.classList.remove('active');
        
        const dictionaryTab = document.querySelector('.tab-link[data-tab="tab-dictionary"]');
        const dictionaryContent = document.getElementById('tab-dictionary');
        dictionaryTab.classList.add('active');
        dictionaryContent.classList.add('active');
      }

      if (
        dictionaryCurrent.innerHTML &&
        !dictionaryCurrent.querySelector(".placeholder")
      ) {
        const historyItem = document.createElement("div");
        historyItem.classList.add("history-item");
        historyItem.innerHTML = dictionaryCurrent.innerHTML
          .replace(/<h4/g, "<h5")
          .replace(/<\/h4/g, "</h5>");
        dictionaryHistory.prepend(historyItem);
      }

      dictionaryCurrent.innerHTML =
        '<p class="placeholder">AI가 문맥을 파악 중입니다...</p>';

      try {
        const response = await fetch("/api/define", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            word: selectedText,
            context: readerContent.textContent,
          }),
        });
        const data = await response.json();
        dictionaryCurrent.innerHTML = `<h4>${data.word}</h4><p>${data.definition}</p>`;
      } catch (error) {
        dictionaryCurrent.innerHTML = "<p>단어 뜻 분석에 실패했습니다.</p>";
      }
    }
  });

  // 10. 모달 닫기 이벤트들
  choiceModalCloseBtn.addEventListener("click", () => choiceModal.close());
  choiceModal.addEventListener(
    "click",
    (e) => e.target === choiceModal && choiceModal.close()
  );
  readerCloseBtn.addEventListener("click", () => {
    readerView.classList.remove("visible");
    setTimeout(() => readerView.classList.add("hidden"), 300);
  });
  
  // 11. 사이드바 탭 기능
  sidebarTabs.forEach(tab => {
      tab.addEventListener("click", () => {
          sidebarTabs.forEach(t => t.classList.remove("active"));
          tabContents.forEach(c => c.classList.remove("active"));
          tab.classList.add("active");
          document.getElementById(tab.dataset.tab).classList.add("active");
      });
  });

  // 12. 페이지가 처음 로드될 때 'home' 카테고리 뉴스를 자동으로 불러옵니다.
  fetchAndRenderNews("home");
});