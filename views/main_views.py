from flask import Blueprint, render_template

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    """메인 페이지를 보여주는 함수"""
    return render_template('index.html')