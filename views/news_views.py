import os
from flask import Blueprint, jsonify, session
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
bp = Blueprint('news', __name__, url_prefix='/api/news')

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@bp.route('/view/<article_id>', methods=['POST'])
def increment_view_count(article_id):
    """기사 ID를 받아 조회수를 1 증가시키고, 읽은 기록을 남기는 API"""
    try:
        # 1. DB 함수(increment_views)를 호출하여 조회수 1 증가 (기존 방식 유지)
        supabase.rpc('increment_views', {'article_id_text': article_id}).execute()
        
        # ▼▼▼ '최근 읽은 기사' 기록 로직 추가 ▼▼▼
        # 2. 로그인 상태인지 확인하고, '읽은 기사'로 기록합니다.
        if 'user' in session:
            try:
                # upsert를 사용하면 중복 오류 없이 안전하게 기록을 추가/갱신합니다.
                supabase.table('user_read_history').upsert({
                    'user_id': session['user']['id'],
                    'article_id': article_id,
                    'read_at': 'now()'
                }).execute()
                print(f"✅ User {session['user']['id'][:5]}... read article {article_id}")
            except Exception as e:
                print(f"Read history logging failed: {e}")
        
        return {"status": "success"}, 200
        
    except Exception as e:
        print(f"Failed to update view count for {article_id}: {e}")
        return {"status": "error", "message": str(e)}, 500