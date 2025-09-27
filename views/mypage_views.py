import os
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
bp = Blueprint('mypage', __name__, url_prefix='/mypage')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bp.route('/')
def mypage():
    """마이페이지 렌더링. DB에서 최신 사용자 정보와 기록을 가져옴"""
    user_info = session.get('user')
    if not user_info:
        return redirect(url_for('auth.login'))

    user_id = user_info['id']

    # ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
    # DB의 profiles 테이블에서 최신 사용자 정보를 가져옵니다.
    try:
        profile_res = supabase.table('profiles').select('full_name, user_level').eq('id', user_id).single().execute()
        if profile_res.data:
            # 기존 세션 정보에 최신 프로필 정보를 덮어씁니다.
            user_info.update(profile_res.data)
            # Flask 세션 자체를 새로운 정보로 갱신합니다.
            session['user'] = user_info
    except Exception as e:
        print(f"Mypage profile fetching failed: {e}")
    # ▲▲▲ 핵심 수정 끝 ▲▲▲

    read_history = []
    word_history = []
    
    try:
        # 최근 읽은 기사 5개
        read_res = supabase.table('user_read_history').select('*, articles(*)').eq('user_id', user_id).order('read_at', desc=True).limit(5).execute()
        read_history = [item['articles'] for item in read_res.data if item.get('articles')]

        # 최근 검색한 단어 5개
        word_res = supabase.table('user_word_history').select('*').eq('user_id', user_id).order('searched_at', desc=True).limit(5).execute()
        word_history = word_res.data
        
    except Exception as e:
        print(f"My Page history fetching failed: {e}")

    return render_template('mypage.html', 
                           user=user_info, 
                           read_history=read_history, 
                           word_history=word_history)

# --- '더보기'를 위한 API들 ---

@bp.route('/api/history/articles')
def get_all_read_history():
    """지난 7일간의 읽은 기사 전체 기록을 반환"""
    user_info = session.get('user')
    if not user_info: return jsonify({'error': '로그인이 필요합니다.'}), 401

    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    # ▼▼▼ 정렬 기준 컬럼을 'read_at'으로 수정 ▼▼▼
    response = supabase.table('user_read_history').select('*, articles(*)') \
        .eq('user_id', user_info['id']) \
        .gte('read_at', seven_days_ago) \
        .order('read_at', desc=True).execute()
    
    article_list = [item['articles'] for item in response.data if item.get('articles')]
    return jsonify(article_list)

@bp.route('/api/history/words')
def get_all_word_history():
    """지난 7일간의 찾아본 단어 전체 기록을 반환"""
    user_info = session.get('user')
    if not user_info: return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    # ▼▼▼ 정렬 기준 컬럼을 'searched_at'으로 수정 ▼▼▼
    response = supabase.table('user_word_history').select('*') \
        .eq('user_id', user_info['id']) \
        .gte('searched_at', seven_days_ago) \
        .order('searched_at', desc=True).execute()
    return jsonify(response.data)

@bp.route('/api/update_level', methods=['POST'])
def update_user_level():
    user_info = session.get('user')
    if not user_info:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        data = request.get_json()
        new_level = data.get('level')
        user_id = user_info['id']
        
        # ▼▼▼ auth.users 대신 public.profiles 테이블을 업데이트합니다 ▼▼▼
        supabase.table('profiles').update({'user_level': new_level}).eq('id', user_id).execute()

        # Flask 세션 정보도 새로운 레벨로 업데이트
        if 'user' in session:
            session['user']['user_level'] = new_level # 세션 구조에 맞게 수정
            session.modified = True
            
        return jsonify({'success': True, 'message': f'레벨이 {new_level}로 업데이트되었습니다.'}), 200

    except Exception as e:
        print(f"Level update failed: {e}")
        return jsonify({'error': '레벨 업데이트에 실패했습니다.'}), 500