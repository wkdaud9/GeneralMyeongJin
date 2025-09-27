document.addEventListener('DOMContentLoaded', function() {
    // 탭 기능 초기화
    document.getElementById('find-id').style.display = 'block';

    // 모달 관련 요소 초기화
    const openModalBtn = document.getElementById('open-modal-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalBackdrop = document.getElementById('modal-backdrop');

    // 모달 열기
    openModalBtn.addEventListener('click', function() {
        // 여기에 실제 비밀번호 재설정 요청 로직(fetch 등)을 넣을 수 있습니다.
        // 요청 성공 시 아래 코드가 실행되도록 합니다.
        modalBackdrop.classList.add('active');
        document.body.classList.add('modal-open');
    });

    // 모달 닫기 함수
    function closeModal() {
        modalBackdrop.classList.remove('active');
        document.body.classList.remove('modal-open');
    }

    // 닫기 버튼 클릭 시
    closeModalBtn.addEventListener('click', closeModal);

    // 모달 바깥 영역(어두운 배경) 클릭 시
    modalBackdrop.addEventListener('click', function(event) {
        if (event.target === modalBackdrop) {
            closeModal();
        }
    });
});

// 탭 전환 함수 (전역 스코프에 있어야 HTML의 onclick에서 호출 가능)
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
    evt.currentTarget.className += " active";
}