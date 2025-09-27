import os
from dotenv import load_dotenv
from flask import Flask
from views import scraper_views, main_views, news_views, llm_views, auth_views, mypage_views, timeline_views
from apscheduler.schedulers.background import BackgroundScheduler
from views.scraper_views import run_all_scrapes # ◀ 크롤링 함수 import
from datetime import datetime, timezone # ◀ timezone도 함께 import하여 정확한 시간대 설정

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = Flask(__name__)

# .env 파일에 저장된 SECRET_KEY를 Flask 앱의 설정으로 가져옵니다.
app.secret_key = os.getenv("SECRET_KEY")

# 모든 Blueprint를 등록합니다.
app.register_blueprint(main_views.bp)
app.register_blueprint(scraper_views.bp)
app.register_blueprint(news_views.bp)
app.register_blueprint(auth_views.bp)
app.register_blueprint(llm_views.bp)
app.register_blueprint(mypage_views.bp)
app.register_blueprint(timeline_views.bp)


# 스케줄링될 작업을 정의합니다.
def scheduled_job():
    """Flask의 app context 안에서 크롤링 함수를 실행"""
    with app.app_context():
        run_all_scrapes()

if __name__ == '__main__':
    # 백그라운드 스케줄러를 생성하고 작업을 등록합니다.
    # timezone을 'Asia/Seoul'로 명확히 지정합니다.
    scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')
    
    # next_run_time=datetime.now(timezone.utc) 옵션을 추가하여, 서버가 시작되자마자 작업을 1회 즉시 실행합니다.
    # 한국 시간으로 즉시 실행하고 싶다면, `datetime.now()`만 사용해도 무방하지만, 
    # `timezone='Asia/Seoul'`을 명시했으므로 `datetime.now()`는 해당 타임존을 따릅니다.
    scheduler.add_job(scheduled_job, 'interval', minutes=30, next_run_time=datetime.now())
    
    scheduler.start()
    
    # 스케줄러의 이중 실행을 방지하기 위해 debug 모드를 끄고 use_reloader=False로 실행하는 것이 안정적입니다.
    # 개발 중에는 debug=True를 사용하고 use_reloader=False를 사용하면 편리합니다.
    app.run(debug=False, use_reloader=False)