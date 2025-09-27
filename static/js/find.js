// 탭 전환 함수
function openTab(evt, tabName) {
  let i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tab-button");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";

  // evt가 null이 아닐 때만 currentTarget을 사용하도록 수정
  if (evt) {
    evt.currentTarget.className += " active";
  } else {
    // evt가 없으면(페이지 로드 시), tabName으로 버튼을 찾아 active 클래스 추가
    document
      .querySelector(`.tab-button[onclick*="'${tabName}'"]`)
      .classList.add("active");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // 모달 관련 요소 초기화
  const openModalBtn = document.getElementById("open-modal-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const modalBackdrop = document.getElementById("modal-backdrop");

  // ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
  // 1. URL에서 'tab' 파라미터 값을 읽어옵니다.
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");

  // 2. 파라미터 값에 따라 해당 탭을 엽니다.
  if (tab === "pw") {
    openTab(null, "find-pw");
  } else {
    // 기본값 또는 tab=id일 경우 '아이디 찾기' 탭을 엽니다.
    openTab(null, "find-id");
  }
  // ▲▲▲ 핵심 수정 끝 ▲▲▲

  // 모달 열기
  if (openModalBtn) {
    openModalBtn.addEventListener("click", function () {
      modalBackdrop.classList.add("active");
      document.body.classList.add("modal-open");
    });
  }

  // 모달 닫기 함수
  function closeModal() {
    modalBackdrop.classList.remove("active");
    document.body.classList.remove("modal-open");
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", closeModal);
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", function (event) {
      if (event.target === modalBackdrop) {
        closeModal();
      }
    });
  }
});
