import os
import requests
from flask import Blueprint, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timezone
import re

load_dotenv()
bp = Blueprint('timeline', __name__, url_prefix='/api/timeline')

# --- 클라이언트 초기화 ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@bp.route('/<article_id>')
def get_timeline(article_id):
    """AI로 검색어를 추출하고, 네이버 API로 '과거 기사'만 찾아 최신순으로 정렬하는 API"""
    try:
        # 1. DB에서 현재 기사의 제목과 생성 날짜 가져오기
        res = supabase.table('articles').select('title, article_id').eq('article_id', article_id).single().execute()
        if not res.data:
            return jsonify({'error': '기사 정보를 찾을 수 없습니다.'}), 404
        
        current_article = res.data
        title = current_article.get('title', '')
        
        # 현재 기사의 날짜를 'YYYYMMDD' 형식으로 추출
        current_article_date_str = current_article['article_id'][:8]
        
        # 2. AI(Gemini)에게 제목을 주고 검색어 추출 요청
        model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        prompt = f"다음 뉴스 제목에서 가장 핵심적인 인물, 사건, 장소 키워드를 2~3개만 쉼표(,)로 구분해서 추출해줘. 다른 설명은 절대 하지마. 예시: 조희대, 대법원, 청문회\n\n제목: \"{title}\""
        
        ai_response = model.generate_content(prompt)
        search_query = ai_response.text.strip().replace(',', ' ')

        if not search_query:
            return jsonify([])

        # 3. 네이버 뉴스 검색 API 호출 (날짜순으로 정렬)
        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }
        # sort='date'로 날짜순(최신순) 정렬, display=20으로 넉넉하게 가져옴
        params = {'query': search_query, 'display': 20, 'sort': 'date'} 
        
        search_res = requests.get('https://openapi.naver.com/v1/search/news.json', headers=headers, params=params)
        search_res.raise_for_status()
        
        # 4. 결과 필터링 및 정렬
        timeline_articles = []
        for item in search_res.json().get('items', []):
            pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
            
            # ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
            # 현재 기사보다 '과거' 날짜의 기사만 타임라인에 추가합니다.
            if pub_date.strftime('%Y%m%d') < current_article_date_str:
                clean_title = re.sub('<[^<]+?>', '', item['title'])
                timeline_articles.append({
                    'title': clean_title,
                    'datetime': pub_date.strftime('%Y-%m-%d'),
                    'url': item['link']
                })

        timeline_articles.sort(key=lambda x: x['datetime'])
        # API가 이미 날짜순으로 정렬해주었으므로, 별도의 정렬은 필요 없습니다.
        return jsonify(timeline_articles)

    except Exception as e:
        print(f"Timeline API Error: {e}")
        return jsonify({'error': '타임라인을 만드는 중 오류가 발생했습니다.'}), 500