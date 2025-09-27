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

@bp.route('/find/')
def find_account():
    """아이디/비밀번호 찾기 페이지를 보여주는 함수"""
    return render_template('find.html')


# --- 회원가입 API (수정) ---
@bp.route('/signup', methods=['POST'])
def signup_post():
    """회원가입 폼 데이터를 받아 Supabase에 사용자를 생성하는 API"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        level = data.get('level')
        username = data.get('username')

        if not all([email, password, name, level, username]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400

        res = supabase.auth.sign_up({
            "email": email, "password": password,
            "options": {"data": {'full_name': name, 'user_level': level, 'username': username}}
        })
        
        # 성공 시, 바로 성공 응답을 반환
        return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'}), 200
        
    except AuthApiError as e:
        # Supabase에서 오는 인증 에러 (예: "User already registered")를 직접 처리
        return jsonify({'error': e.message}), 400
    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

# ▼▼▼ 아이디 찾기 API 추가 ▼▼▼
@bp.route('/find-id', methods=['POST'])
def find_id_post():
    """이름과 이메일을 받아 아이디를 찾아주는 API"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return jsonify({'error': '이름과 이메일을 모두 입력해주세요.'}), 400
        
        # profiles 테이블에서 이름과 이메일이 일치하는 사용자의 username을 찾음
        res = supabase.table('profiles').select('username').eq('full_name', name).eq('email', email).execute()

        # 데이터가 리스트 안에 존재하는지 확인합니다.
        if res.data:
            # 리스트의 첫 번째 항목을 반환합니다.
            return jsonify(res.data[0]), 200
        else:
            # 리스트가 비어있으면, 일치하는 사용자가 없는 것입니다.
            return jsonify({'error': '일치하는 사용자를 찾을 수 없습니다.'}), 404
            
    except Exception as e:
        print(f"Find ID Error: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
    
    # ▼▼▼ 비밀번호 재설정(찾기) API 추가 ▼▼▼
@bp.route('/reset-password', methods=['POST'])
def reset_password_post():
    """이메일을 받아 비밀번호 재설정 링크를 보내는 API"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': '이메일을 입력해주세요.'}), 400
        
        # Supabase Auth를 사용해 비밀번호 재설정 이메일 발송
        supabase.auth.reset_password_email(email)
        
        return jsonify({'success': True, 'message': '비밀번호 재설정 링크를 이메일로 보냈습니다.'}), 200
            
    except Exception as e:
        print(f"Password Reset Error: {e}")
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
        if str(e) == "Invalid login credentials":
            return jsonify({'error': '이메일 또는 비밀번호를 확인해주세요.'}), 401
        else:
            return jsonify({'error': str(e)}), 401
        
# --- 로그아웃 API ---
@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))