from flask import Flask
# auth_views를 추가로 import 합니다.
from views import main_views, auth_views, scraper_views

app = Flask(__name__)

# 메인 페이지와 인증 Blueprint를 등록합니다.
app.register_blueprint(main_views.bp)
app.register_blueprint(auth_views.bp) # ◀ 이 줄이 추가되어야 합니다.
app.register_blueprint(scraper_views.bp) # ◀ 이 줄을 추가합니다.

if __name__ == '__main__':
    app.run(debug=True)