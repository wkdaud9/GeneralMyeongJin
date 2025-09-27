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
    """기사 ID를 받아 조회수를 1 증가시키는 API"""
    try:
        # DB 함수(increment_views)를 호출하여 조회수 1 증가
        supabase.rpc('increment_views', {'article_id_text': article_id}).execute()        
        return {"status": "success"}, 200
        
    except Exception as e:
        print(f"Failed to update view count for {article_id}: {e}")
        return {"status": "error", "message": str(e)}, 500