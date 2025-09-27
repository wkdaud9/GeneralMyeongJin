import os
from dotenv import load_dotenv
from flask import Flask
from views import scraper_views, main_views, news_views, llm_views, auth_views, mypage_views

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = Flask(__name__)

# ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
# .env 파일에 저장된 SECRET_KEY를 Flask 앱의 설정으로 가져옵니다.
app.secret_key = os.getenv("SECRET_KEY")
# ▲▲▲ 이 줄이 반드시 필요합니다 ▲▲▲
# 모든 Blueprint를 등록합니다.

app.register_blueprint(main_views.bp)
app.register_blueprint(scraper_views.bp)
app.register_blueprint(news_views.bp)
app.register_blueprint(auth_views.bp) # ◀ auth_views.bp 등록 코드를 추가합니다.
app.register_blueprint(llm_views.bp)
app.register_blueprint(mypage_views.bp)


if __name__ == '__main__':
    app.run(debug=True)