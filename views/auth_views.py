from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from gotrue.errors import AuthApiError

load_dotenv()
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- 페이지 보여주기 함수들 ---
@bp.route('/login/')
def login():
    return render_template('login.html')

@bp.route('/signup/')
def signup():
    return render_template('signup.html')

@bp.route('/level-test/')
def level_test():
    return render_template('level-test.html')


# --- 회원가입 API ---
@bp.route('/signup', methods=['POST'])
def signup_post():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        level = data.get('level')

        if not all([email, password, name, level]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400

        res = supabase.auth.sign_up({
            "email": email, "password": password,
            "options": {"data": {'full_name': name, 'user_level': level}}
        })
        
        return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'}), 200
        
    except AuthApiError as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500


# --- 로그인 API (수정) ---
@bp.route('/login', methods=['POST'])
def login_post():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': '이메일과 비밀번호를 입력해주세요.'}), 400

        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        session['user'] = res.user.model_dump()
        
        return jsonify({'success': True, 'message': '로그인 성공!'}), 200
        # ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
        # Supabase 에러 메시지 내용에 따라 분기 처리
        
            
    except Exception as e:
        if e.message == "Invalid login credentials":
            return jsonify({'error': '이메일 또는 비밀번호를 확인해주세요.'}), 401
        else:
            return jsonify({'error': e.message}), 401
        
# --- 로그아웃 API ---
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))