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

  if (evt) {
    evt.currentTarget.className += " active";
  } else {
    document
      .querySelector(`.tab-button[onclick*="'${tabName}'"]`)
      .classList.add("active");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // URL 파라미터를 확인하여 시작 탭을 결정
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get("tab");

  if (tab === "pw") {
    openTab(null, "find-pw");
  } else {
    openTab(null, "find-id");
  }

  // --- 아이디 찾기 로직 ---
  const findIdForm = document.getElementById("find-id-form");
  const resultModal = document.getElementById("result-modal");
  const modalMessage = document.getElementById("modal-message-text");
  const closeModalBtn = document.getElementById("close-modal-btn");

  if (findIdForm) {
    findIdForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = {
        name: document.getElementById("find-name").value,
        email: document.getElementById("email-for-id").value,
      };

      try {
        const response = await fetch("/auth/find-id", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
        const result = await response.json();

        if (response.ok) {
          modalMessage.textContent = `회원님의 아이디는 [ ${result.username} ] 입니다.`;
          resultModal.classList.add("active");
        } else {
          Swal.fire("아이디 찾기 실패", result.error, "error");
        }
      } catch (error) {
        Swal.fire("오류", "서버와 통신 중 오류가 발생했습니다.", "error");
      }
    });
  }

  // 아이디 찾기 결과 모달 닫기
  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", () => {
      resultModal.classList.remove("active");
    });
  }
  if (resultModal) {
    resultModal.addEventListener("click", (e) => {
      if (e.target === resultModal) {
        resultModal.classList.remove("active");
      }
    });
  }

  // --- 비밀번호 찾기 로직 ---
  const findPwForm = document.getElementById("find-pw-form");

  if (findPwForm) {
    findPwForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const email = document.getElementById("email-for-pw").value;
      const formData = { email: email };

      try {
        const response = await fetch("/auth/reset-password", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
        const result = await response.json();

        if (response.ok) {
          Swal.fire({
            icon: "success",
            title: "전송 완료",
            text: "입력하신 이메일로 비밀번호 재설정 링크를 보냈습니다.",
          });
        } else {
          Swal.fire("오류", result.error, "error");
        }
      } catch (error) {
        Swal.fire("오류", "서버와 통신 중 오류가 발생했습니다.", "error");
      }
    });
  }
});
