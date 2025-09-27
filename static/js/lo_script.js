// 커스텀 드롭다운 메뉴 제어
const selectDisplay = document.getElementById('level-display');
const selectOptions = document.getElementById('level-options');
const hiddenInput = document.getElementById('level');

selectDisplay.addEventListener('click', function() {
    selectOptions.classList.toggle('hidden');
});

selectOptions.addEventListener('click', function(e) {
    if (e.target.classList.contains('option-item')) {
        const selectedText = e.target.innerText;
        const selectedValue = e.target.dataset.value;

        selectDisplay.innerText = selectedText;
        hiddenInput.value = selectedValue;
        selectOptions.classList.add('hidden');
    }
});

// 외부 클릭 시 드롭다운 닫기
document.addEventListener('click', function(e) {
    if (!selectDisplay.contains(e.target) && !selectOptions.contains(e.target)) {
        selectOptions.classList.add('hidden');
    }
});