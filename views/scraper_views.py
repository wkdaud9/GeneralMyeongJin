import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from flask import Blueprint, jsonify
import re
from dotenv import load_dotenv
import time
import google.generativeai as genai # 🌟 추가: Gemini AI 라이브러리 임포트
import pytz # 🌟 추가: 시간대 처리를 위한 pytz 라이브러리
from datetime import datetime # 🌟 추가: datetime 임포트

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 'scraper'라는 이름의 Blueprint를 생성합니다.
bp = Blueprint('scraper', __name__, url_prefix='/scrape')

# --- Supabase 클라이언트 초기화 ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Gemini AI 클라이언트 초기화 (크롤러에서 사용) 🌟 추가 🌟 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')

# --- 크롤링할 카테고리 URL 정의 ---
NEWS_CATEGORIES = {
    'home': 'https://news.daum.net/',
    'economy': 'https://news.daum.net/economic',
    'politics': 'https://news.daum.net/politics',
    'international': 'https://news.daum.net/foreign',
    'it': 'https://news.daum.net/digital'
}

def extract_keywords_with_ai(title):
    """AI를 사용하여 뉴스 제목에서 핵심 키워드를 추출합니다. 🌟 추가 🌟"""
    prompt = f"다음 뉴스 제목에서 가장 핵심적인 인물, 사건, 장소 키워드를 2~3개만 쉼표(,)로 구분해서 추출해줘. 다른 설명은 절대 하지마. 예시: 조희대, 대법원, 청문회\n\n제목: \"{title}\""
    try:
        response = ai_model.generate_content(prompt)
        keywords = response.text.strip()
        print(f"[AI 추출] '{title}' -> 키워드: {keywords}")
        return keywords
    except Exception as e:
        print(f"[AI 에러] 키워드 추출 실패 (제목: {title}): {e}")
        return "" # 실패 시 빈 문자열 반환


def get_article_details(url, category):
    """(수정) 본문 없이 기사의 기본 정보, URL, AI 추출 키워드를 추출하는 함수"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        match = re.search(r'v\.daum\.net\/v\/(\w+)', url)
        article_id = match.group(1) if match else url.split('/')[-1]

        title_tag = soup.find("h3", class_="tit_view")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
        
        thumbnail_url = "썸네일 없음"
        thumbnail_tag = soup.find("meta", property="og:image")
        if thumbnail_tag:
            thumbnail_url = thumbnail_tag['content']
        else:
            img_tag = soup.find("img", class_="thumb_g_article")
            if img_tag:
                thumbnail_url = img_tag['src']

        extracted_keywords = extract_keywords_with_ai(title)

        # 🌟🌟🌟 핵심 변경: 현재 시간을 created_at으로 직접 추가 🌟🌟🌟
        # 한국 시간대로 설정 (pytz 필요)
        korea_tz = pytz.timezone('Asia/Seoul')
        current_time_korea = datetime.now(korea_tz)

        return {
            'article_id': article_id,
            'title': title,
            'thumbnail': thumbnail_url,
            'category': category,
            'url': url,
            'extracted_keywords': extracted_keywords,
            'created_at': current_time_korea.isoformat() # ISO 8601 형식으로 저장
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def get_news_urls(list_url):
    """중복을 제거하여 뉴스 기사 URL을 수집하는 함수"""
    response = requests.get(list_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, "html.parser")
    
    unique_urls = set()
    # 다음 뉴스 페이지 구조에 맞는 선택자 조합
    link_selectors = [
        "a.link_txt",          # 대부분의 기사 제목 링크
        "a.link_mainnews",     # 메인 영역 큰 기사 링크
        "a.item_newsheadline2",# 특정 섹션의 헤드라인 (더 이상 사용 안될 수 있음)
        "a.link_g"             # 다른 유형의 기사 링크
    ]
    
    article_links = soup.select(', '.join(link_selectors))
    
    for link in article_links:
        href = link.get('href')
        if href and href.startswith('https://v.daum.net/v/'):
            unique_urls.add(href)

    # 넉넉하게 15개 정도 가져와서 중복 제거 후 사용
    return list(unique_urls)[:15] # 가져오는 URL 개수 증가 (top 10에서 top 15로)

# `run_all_scrapes` 함수만 사용하도록 구조 변경
def run_all_scrapes():
    """모든 카테고리를 크롤링하고 DB에 저장하는 순수 파이썬 함수"""
    print("="*30)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 스케줄링된 크롤링 시작...")
    
    all_scraped_data = []
    
    for category, url in NEWS_CATEGORIES.items():
        print(f"\n--- 📰 '{category}' 카테고리 크롤링 시작 ---")
        
        target_urls = get_news_urls(url)
        print(f"✅ URL {len(target_urls)}개 수집 완료.")
        
        for article_url in target_urls:
            details = get_article_details(article_url, category)
            if details and details['title'] != "제목 없음":
                all_scraped_data.append(details)
            # AI API 호출 제한을 위해 잠시 대기
            time.sleep(1) # 각 기사 상세 크롤링 및 AI 호출 사이에 1초 대기

    if all_scraped_data:
        # DB에 저장하기 전, 전체 데이터에서 중복 기사를 최종적으로 제거합니다.
        # article_id를 키로 사용하여 중복 제거
        unique_articles = {article['article_id']: article for article in all_scraped_data}
        final_unique_data = list(unique_articles.values())
        
        print(f"\n💾 수집된 전체 뉴스 {len(all_scraped_data)}개 중, 중복을 제외한 {len(final_unique_data)}개를 Supabase DB에 저장합니다...")
        try:
            # upsert를 사용하여 article_id가 중복될 경우 업데이트, 없으면 삽입
            supabase.table('articles').upsert(final_unique_data, on_conflict='article_id').execute()
            print("✅ 데이터 저장(또는 업데이트) 성공!")
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
            print(f"오류 내용: {e}")
    else:
        print("🤔 새로 수집된 뉴스가 없습니다.")
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 스케줄링된 크롤링 종료.")
    print("="*30)


# 🌟 API 엔드포인트는 run_all_scrapes 함수를 호출하도록 변경 🌟
# `/scrape/start` 경로로 요청이 오면 `run_all_scrapes`를 실행하고 결과를 반환
@bp.route('/start')
def start_scraping_route():
    """테스트를 위해 수동으로 크롤링을 실행시키는 API"""
    run_all_scrapes()
    return jsonify({'status': 'success', 'message': '크롤링을 수동으로 실행했습니다.'})

# `refetch_article` 함수는 `run_all_scrapes`와 기능적으로 중복되거나, 
# AI 키워드 추출까지 포함해야 한다면 `get_article_details`를 사용하는 방식으로 변경해야 합니다.
# 현재 `get_article_details`에 AI 추출이 포함되어 있으므로, 
# 이 `refetch_article` 함수는 그대로 두어도 AI 키워드 추출이 포함된 채로 업데이트될 것입니다.
@bp.route('/refetch/<article_id>')
def refetch_article(article_id):
    """기사 ID를 받아 해당 기사만 다시 크롤링하고 DB에 업데이트하는 API"""
    if not article_id:
        return jsonify({'status': 'error', 'message': '기사 ID가 필요합니다.'}), 400

    # Daum 뉴스 article_id는 보통 15자리 숫자이므로, URL을 구성합니다.
    target_url = f"https://v.daum.net/v/{article_id}" 
    print(f"--- 🔄 특정 기사 재수집 시작: {target_url} ---")
    
    # 재수집 시 카테고리는 DB에서 조회하거나, 임시로 'manual_refetch'로 지정할 수 있습니다.
    # 여기서는 'manual_refetch'로 임시 지정하여 get_article_details를 호출합니다.
    details = get_article_details(target_url, 'manual_refetch') # 🌟 AI 키워드 추출 포함 🌟

    if details and details['title'] != "제목 없음":
        print(f"✅ 재수집 성공. DB에 업데이트합니다...")
        try:
            # upsert를 사용하여 기존 데이터를 덮어씁니다.
            supabase.table('articles').upsert(details, on_conflict='article_id').execute()
            print("✅ 데이터 업데이트 성공!")
            return jsonify({'status': 'success', 'message': f"기사({article_id})를 성공적으로 재수집하고 업데이트했습니다."})
        except Exception as e:
            print(f"❌ 데이터 업데이트 실패: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
    return jsonify({'status': 'error', 'message': '해당 기사를 수집하는 데 실패했습니다. ID를 확인하거나 URL 패턴이 변경되었을 수 있습니다.'}), 500