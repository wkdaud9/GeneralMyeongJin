import os
import requests
from flask import Blueprint, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
# import google.generativeai as genai # 🌟 제거: AI 모델은 크롤러에서만 사용
from datetime import datetime, timezone
import re

load_dotenv()
bp = Blueprint('timeline', __name__, url_prefix='/api/timeline')

# --- 클라이언트 초기화 ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # 🌟 제거: AI 모델은 크롤러에서만 사용
# genai.configure(api_key=GEMINI_API_KEY) # 🌟 제거: AI 모델은 크롤러에서만 사용

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

@bp.route('/<article_id>')
def get_timeline(article_id):
    """DB에 저장된 키워드로 네이버 API를 호출하여 타임라인을 생성하는 API"""
    try:
        # 1. DB에서 현재 기사의 제목, article_id (날짜 정보), 🌟추출된 키워드🌟 가져오기
        res = supabase.table('articles').select('title, article_id, extracted_keywords').eq('article_id', article_id).single().execute()
        if not res.data:
            return jsonify({'error': '기사 정보를 찾을 수 없습니다.'}), 404
        
        current_article = res.data
        title = current_article.get('title', '')
        # 🌟🌟🌟 핵심 변경: DB에서 미리 추출된 키워드를 가져와 사용 🌟🌟🌟
        search_query_from_db = current_article.get('extracted_keywords', '') 
        
        # 현재 기사의 날짜를 'YYYYMMDD' 형식으로 추출 (article_id 앞 8자리)
        current_article_date_str = current_article['article_id'][:8]
        
        # 2. AI 키워드 추출 로직 제거 🌟🌟🌟
        # 이전에 여기에 있던 genai.GenerativeModel 호출 코드가 이제 필요 없습니다.
        search_query = search_query_from_db.replace(',', ' ') # 쉼표를 공백으로 바꿔 네이버 검색어 형식에 맞춤

        if not search_query:
            # DB에 키워드가 없으면 빈 타임라인 반환
            return jsonify([])

        # 3. 네이버 뉴스 검색 API 호출 (날짜순으로 정렬)
        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }
        # sort='date'로 날짜순(최신순) 정렬, display=20으로 넉넉하게 가져옴
        params = {'query': search_query, 'display': 20, 'sort': 'date'} 
        
        search_res = requests.get('https://openapi.naver.com/v1/search/news.json', headers=headers, params=params)
        search_res.raise_for_status() # HTTP 오류 발생 시 예외 발생

        # 4. 결과 필터링 및 정렬
        timeline_articles = []
        for item in search_res.json().get('items', []):
            # 네이버 API의 pubDate 형식 파싱: 'Mon, 27 May 2024 10:00:00 +0900'
            # %z는 UTC 오프셋을 처리하지만, Naver는 +0900으로 고정된 경우가 많음.
            # 정확한 비교를 위해 pubDate를 datetime 객체로 변환
            pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S %z')
            
            # 현재 기사보다 '과거' 날짜의 기사만 타임라인에 추가합니다.
            # 날짜 문자열(YYYYMMDD)을 비교하는 것이 가장 간단하고 명확합니다.
            if pub_date.strftime('%Y%m%d') < current_article_date_str:
                clean_title = re.sub('<[^<]+?>', '', item['title']) # HTML 태그 제거
                timeline_articles.append({
                    'title': clean_title,
                    'datetime': pub_date.strftime('%Y-%m-%d'), # 출력 형식은 YYYY-MM-DD
                    'url': item['link']
                })

        # 날짜(datetime)를 기준으로 리스트를 오름차순(오래된 순)으로 정렬합니다.
        # 네이버 API가 이미 최신순으로 정렬해서 주지만, '과거 기사'만 뽑은 후 다시 오래된 순으로 정렬하는 것이 타임라인 흐름상 자연스러움
        timeline_articles.sort(key=lambda x: x['datetime'])

        return jsonify(timeline_articles)

    except Exception as e:
        print(f"Timeline API Error for article_id {article_id}: {e}")
        return jsonify({'error': '타임라인을 만드는 중 오류가 발생했습니다.'}), 500