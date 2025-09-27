// quiz.js

// 12개의 질문 데이터 (2개의 신조어 문제 추가)
const questions = [
  {
    question:
      "우리 아파트의 '쓰레기 분리수거'는 매주 화요일과 목요일 저녁 8시부터 10시까지 진행됩니다. 쓰레기 분리수거는 언제 이루어지나요?",
    answerOptions: [
      { text: "매주 화요일 아침", isCorrect: false },
      { text: "매주 목요일 오후", isCorrect: false },
      { text: "매주 화요일과 목요일 저녁", isCorrect: true },
      { text: "매일 저녁", isCorrect: false },
    ],
    level: "Level 1",
  },
  {
    question:
      "OOO 어린이 과학 체험전은 12월 23일부터 25일까지 운영됩니다. 선착순 100명에게 무료 입장 혜택이 주어집니다. 무료 입장 혜택을 받기 위해 필요한 조건은 무엇인가요?",
    answerOptions: [
      { text: "12월 23일에 방문", isCorrect: false },
      { text: "어린이 동반", isCorrect: false },
      { text: "과학 체험전 관람", isCorrect: false },
      { text: "선착순 100명 안에 들 것", isCorrect: true },
    ],
    level: "Level 1",
  },
  {
    question:
      "101번 버스 시간표: 시청역 출발 오전 7시 00분, 7시 30분, 8시 00분, 8시 40분. 오전 8시 10분경에 버스를 타려면 가장 가까운 시간은 언제인가요?",
    answerOptions: [
      { text: "오전 8시 00분", isCorrect: false },
      { text: "오전 8시 40분", isCorrect: true },
      { text: "오전 7시 30분", isCorrect: false },
      { text: "오전 7시 00분", isCorrect: false },
    ],
    level: "Level 1",
  },
  {
    question:
      "OOO 알약은 식후 30분 뒤에 복용하십시오. 1회 1알씩, 하루 3번 드세요. 이 약은 하루에 총 몇 알을 먹어야 하나요?",
    answerOptions: [
      { text: "1알", isCorrect: false },
      { text: "2알", isCorrect: false },
      { text: "3알", isCorrect: true },
      { text: "4알", isCorrect: false },
    ],
    level: "Level 1",
  },
  {
    question: "다음 문장에서 밑줄 친 '갓성비'가 의미하는 것은 무엇인가요?",
    answerOptions: [
      { text: "뛰어난 성과를 냈다", isCorrect: false },
      { text: "가격 대비 성능이 매우 좋다", isCorrect: true },
      { text: "가치 있는 것을 가졌다", isCorrect: false },
      { text: "신이 주신 성과", isCorrect: false },
    ],
    level: "Level 2",
    isNeologism: true,
  },
  {
    question: "다음 문장에서 밑줄 친 '갑분싸'가 의미하는 상황은 무엇인가요?",
    answerOptions: [
      { text: "갑자기 분위기가 싸해지는 상황", isCorrect: true },
      { text: "갑자기 분위기가 좋아지는 상황", isCorrect: false },
      { text: "갑자기 많은 사람이 모이는 상황", isCorrect: false },
      { text: "갑자기 싸우는 상황", isCorrect: false },
    ],
    level: "Level 2",
    isNeologism: true,
  },
  {
    question: "다음 중 '사실'에 대한 진술로 가장 적절한 것은 무엇인가요?",
    answerOptions: [
      { text: "개인의 의견이나 감정이다.", isCorrect: false },
      { text: "객관적으로 증명될 수 있는 것이다.", isCorrect: true },
      { text: "논쟁의 여지가 있는 주장이다.", isCorrect: false },
      { text: "모두가 옳다고 믿는 내용이다.", isCorrect: false },
    ],
    level: "Level 3",
  },
  {
    question:
      '다음 문장에서 이 글이 전달하고자 하는 핵심적인 메시지는 무엇인가요?<br><br>"최근 온라인 환경에서 가짜 뉴스가 급속도로 확산되고 있다. 이는 사회적 갈등을 심화시키고 공공의 신뢰를 무너뜨릴 수 있어 큰 문제로 지적되고 있다."',
    answerOptions: [
      { text: "온라인 환경의 편리함", isCorrect: false },
      { text: "가짜 뉴스의 위험성", isCorrect: true },
      { text: "사회적 갈등의 원인", isCorrect: false },
      { text: "정보 공유의 중요성", isCorrect: false },
    ],
    level: "Level 3",
  },
  {
    question:
      "한 정치 평론가가 'OOO 후보는 과거에 범죄를 저지른 전과가 있으므로, 그가 내세우는 정책들은 모두 신뢰할 수 없다'고 주장했습니다. 이 주장에서 사용된 비논리적인 방법은 무엇인가요?",
    answerOptions: [
      { text: "흑백 논리 (잘못된 이분법)", isCorrect: false },
      { text: "논점 일탈의 오류", isCorrect: false },
      { text: "성급한 일반화의 오류", isCorrect: false },
      { text: "인신공격의 오류 (피장파장)", isCorrect: true },
    ],
    level: "Level 3",
  },
  {
    question:
      "다음 기사 제목 중 사실을 객관적으로 전달하려는 '중립적인' 표현에 가장 가까운 것은 무엇인가요?",
    answerOptions: [
      { text: "충격! OOO 기업의 '역대급' 신제품 발표", isCorrect: false },
      { text: "OOO 기업, 신제품 '대박' 행진 예감", isCorrect: false },
      { text: "OOO 기업, '혁신적인' 신제품 공개", isCorrect: false },
      { text: "OOO 기업, 신제품 출시 및 주요 기능 공개", isCorrect: true },
    ],
    level: "Level 3",
  },
  {
    question: "다음 신조어 '스몸비'가 의미하는 것은 무엇인가요?",
    answerOptions: [
      { text: "스마트폰을 보며 길을 걷는 사람", isCorrect: true },
      { text: "스마트폰 중독에 빠진 학생", isCorrect: false },
      { text: "혼자 스마트폰으로만 노는 사람", isCorrect: false },
      { text: "스마트폰을 매우 잘 다루는 사람", isCorrect: false },
    ],
    level: "Level 2",
    isNeologism: true,
  },
  {
    question: "다음 중 '퇴준생'의 뜻으로 가장 적절한 것은 무엇인가요?",
    answerOptions: [
      { text: "퇴근을 준비하는 학생", isCorrect: false },
      { text: "퇴직금을 준비하는 사람", isCorrect: false },
      { text: "퇴사를 준비하는 직장인", isCorrect: true },
      { text: "퇴학을 준비하는 사람", isCorrect: false },
    ],
    level: "Level 2",
    isNeologism: true,
  },
];

// HTML 요소 가져오기
const quizContainer = document.getElementById("quiz-container");
const testHeader = document.getElementById("test-header"); // ◀ 헤더 요소 추가
const resultContainer = document.getElementById("result-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const levelTitle = document.getElementById("level-title");
const skillDescription = document.getElementById("skill-description");
const questionText = document.getElementById("question-text");
const answerButtons = document.getElementById("answer-buttons");
const nextButton = document.getElementById("next-button");
const finalScoreText = document.getElementById("final-score-text");
const levelResultText = document.getElementById("level-result-text");
const levelDescriptionText = document.getElementById("level-description-text");
const restartButton = document.getElementById("restart-button");

let currentQuestionIndex = 0;
let score = 0;
let neologismCorrect = 0; // 신조어 문제 정답 수

function startQuiz() {
  currentQuestionIndex = 0;
  score = 0;
  neologismCorrect = 0;
  testHeader.classList.remove("hidden"); // ◀ 퀴즈 시작 시 헤더 보이기
  quizContainer.classList.remove("hidden");
  resultContainer.classList.add("hidden");
  nextButton.classList.add("hidden");
  updateProgress();
  showQuestion();
}

function showQuestion() {
  const currentQuestion = questions[currentQuestionIndex];

  // 문제 제목 및 텍스트 업데이트
  levelTitle.innerText = `문해력 테스트`; // ◀◀◀ 수정
  skillDescription.innerText = `${getSkillDescription(
    currentQuestion.level
  )} 능력 테스트`;
  questionText.innerHTML = currentQuestion.question;

  // 선택지 버튼 생성
  answerButtons.innerHTML = "";
  currentQuestion.answerOptions.forEach((option) => {
    const button = document.createElement("button");
    button.innerText = option.text;
    button.classList.add("btn", "block", "choice");
    if (option.isCorrect) {
      button.dataset.correct = "true";
    }
    button.addEventListener("click", selectAnswer);
    answerButtons.appendChild(button);
  });

  nextButton.classList.add("hidden");
}

function selectAnswer(e) {
  const selectedButton = e.target;
  const isCorrect = selectedButton.dataset.correct === "true";
  const currentQuestion = questions[currentQuestionIndex];

  if (isCorrect) {
    score++;
    selectedButton.classList.add("primary");
    if (currentQuestion.isNeologism) {
      neologismCorrect++;
    }
  } else {
    selectedButton.classList.add("secondary");
    // 신조어 문제 틀리면 특별 처리는 필요 없으나, 레벨 판별 로직에서 사용
  }

  // 다른 선택지 비활성화 및 정답 표시
  Array.from(answerButtons.children).forEach((button) => {
    button.disabled = true;
    if (button.dataset.correct === "true") {
      button.classList.add("primary");
    }
  });

  nextButton.classList.remove("hidden");
  if (currentQuestionIndex === 0 || currentQuestionIndex === 7) {
    setTimeout(() => {
      nextButton.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 100);
  }
}

function showNextQuestion() {
  currentQuestionIndex++;
  updateProgress();
  if (currentQuestionIndex < questions.length) {
    showQuestion();
  } else {
    showResult();
  }
}

async function showResult() {
  // ◀ 함수를 async로 변경
  if (testHeader) testHeader.classList.add("hidden");
  quizContainer.classList.add("hidden");
  resultContainer.classList.remove("hidden");

  levelTitle.innerText = `최종 테스트 결과`;
  skillDescription.innerText = `당신의 뉴스 문해력 수준을 확인하세요.`;

  finalScoreText.innerText = `총 ${questions.length}개 중 ${score}개 정답!`;

  let level = "";
  let description = "";

  // 레벨 판별 로직
  if (score >= 9) {
    if (neologismCorrect >= 2) {
      level = "3"; // 숫자 3으로 변경
      description =
        "축하합니다!\n당신은 뉴스의 숨겨진 맥락과 의도를 파악하고 비판적으로 사고하는 뛰어난 능력을 가졌습니다.\n가장 심도 있는 뉴스 콘텐츠를 추천합니다.";
    } else {
      level = "2"; // 숫자 2로 변경
      description =
        "훌륭합니다!\n당신은 높은 점수를 얻었지만,\n신조어 이해도에서 아쉬움이 남습니다.\n일반적인 뉴스 콘텐츠를 추천합니다.";
    }
  } else if (score >= 5) {
    level = "2"; // 숫자 2로 변경
    description =
      "훌륭합니다!\n당신은 뉴스의 핵심 내용을 잘 이해하고 여러 정보를 연결하는 능력이 뛰어납니다.\n일반적인 뉴스 콘텐츠를 추천합니다.";
  } else {
    level = "1"; // 숫자 1로 변경
    description =
      "걱정하지 마세요!\n당신은 뉴스에 대한 기초적인 정보를 파악하는 능력을 가졌습니다.\n쉽고 간결하게 요약된 뉴스 콘텐츠부터 시작하는 것을 추천합니다.";
  }

  levelResultText.innerText = `Level ${level}`;
  levelDescriptionText.innerText = description;

  // ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
  // 판별된 레벨을 서버로 보내 업데이트 요청
  try {
    await fetch("/mypage/api/update_level", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level: level }),
    });
    // 성공 여부와 관계없이 사용자는 결과를 보고 메인으로 이동하면 됨
  } catch (error) {
    console.error("Failed to update level:", error);
  }
}

function updateProgress() {
  const progress = (currentQuestionIndex / questions.length) * 100;
  progressBar.style.width = `${progress}%`;
  progressText.innerText = `${currentQuestionIndex + 1}/${questions.length}`;
}

function getSkillDescription(level) {
  switch (level) {
    case "Level 1":
      return "기초 정보 파악";
    case "Level 2":
      return "어휘력 및 상식";
    case "Level 3":
      return "비판적 사고 및 사실/의견 구분";
    default:
      return "";
  }
}

// 이벤트 리스너 연결
nextButton.addEventListener("click", showNextQuestion);
restartButton.addEventListener("click", () => {
  // 메인 화면으로 이동
  window.location.href = "/";
});

// 페이지 로드 시 퀴즈 시작
document.addEventListener("DOMContentLoaded", startQuiz);
