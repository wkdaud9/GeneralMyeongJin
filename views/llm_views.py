import os
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request, session
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client
import markdown # ◀ 마크다운 라이브러리 import



load_dotenv()
bp = Blueprint('llm', __name__, url_prefix='/api')

# Gemini 클라이언트 초기화
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Supabase 클라이언트도 필요하므로 추가
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@bp.route('/summarize', methods=['POST'])
def summarize_article():
    data = request.get_json()
    article_url = data.get('url')
    if not article_url:
        return jsonify({'error': 'URL이 필요합니다.'}), 400
    
    try:
        response = requests.get(article_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, "html.parser")
        content_tag = soup.find("div", class_="article_view")
        text_content = content_tag.get_text() if content_tag else ""
        if not text_content:
            return jsonify({'summary': '기사 내용을 불러올 수 없습니다.'})
        
        MAX_CHARS = 15000
        truncated_text = text_content[:MAX_CHARS]
        
        
        user_level = '1'
        if 'user' in session:
            # 로그인 상태라면, DB의 profiles 테이블에서 최신 레벨을 직접 조회
            user_id = session['user']['id']
            try:
                profile_res = supabase.table('profiles').select('user_level').eq('id', user_id).single().execute()
                if profile_res.data:
                    user_level = profile_res.data.get('user_level', '1')
            except Exception as e:
                print(f"Profile level fetching failed: {e}")

        # 2. 레벨별로 다른 프롬프트를 정의합니다.
        prompts = {
            '1': f"다음 뉴스 기사를 8살 아이에게 이야기해준다고 상상하고, 아주 아주 쉬운 단어만 사용해서 무슨 일이 있었는지 설명해줘. 어려운 단어는 모두 다른 쉬운 말로 바꿔주고, 비유를 사용해도 좋아. 대답하지 말고 바로 설명 시작해.:\n\n{truncated_text}",
            '2': f"다음 뉴스 기사를 해당 분야에 익숙하지 않은 일반적인 독자를 위해 쉽고 명료하게 다시 작성해줘 요약이나 소제목은 사용하지 말고, 줄 글 형태로 작성해줘. 전문 용어나 어려운 한자어는 일상적인 표현으로 바꾸고, 복잡한 문장은 나눠서 설명해줘. 기사의 핵심 사실 관계가 잘 드러나도록 재구성해줘.:\n\n{truncated_text}",
            '3': f"다음 뉴스 기사를 심층적으로 분석하는 짧은 해설 기사를 작성해줘. 기사의 핵심 내용을 정리하고, 이 사건이 일어나게 된 배경(Context)과 관련된 용어들을 쉽게 설명해줘. 마지막으로, 이 사건이 앞으로 미칠 영향이나 생각해볼 점에 대한 통찰력 있는 분석을 덧붙여줘.:\n\n{truncated_text}"
        }
        
        # 3. 사용자 레벨에 맞는 프롬프트를 선택합니다.
        prompt = prompts.get(str(user_level), prompts['1']) # 해당 레벨이 없으면 1로 기본 설정

        print(user_level)

        model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        
        ai_response = model.generate_content(prompt, safety_settings=safety_settings)
        summary_html = markdown.markdown(ai_response.text)
        
        return jsonify({'summary': summary_html})
        
    except Exception as e:
        print(f"LLM Summarize API Error: {e}")
        return jsonify({'error': str(e)}), 500
    


@bp.route('/define', methods=['POST'])
def define_word_in_context():
    data = request.get_json()
    word = data.get('word')
    context = data.get('context')

    if not word or not context:
        return jsonify({'error': '단어와 문맥 정보가 모두 필요합니다.'}), 400

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        prompt = f""" 다음 문장에서 단어의 뜻을 설명해 줘. 설명은 국립국어원 표준국어대사전의 정의처럼 간결하고 명확한 스타일로, 한 문장으로 해줘. 출력 형태는 단어를 굳이 말하지 말고, 단어의 뜻만 말해줘. 문장: "{context}" 단어: "{word}" """
        response = model.generate_content(prompt)
        
        # ▼▼▼ 여기가 핵심 수정 부분입니다 ▼▼▼
        
        # 1. AI로부터 받은 순수 텍스트 응답을 변수에 저장
        raw_definition = response.text.strip().replace('**', '')
        
        # 2. 사용자 화면에 보여줄 용도로만 HTML로 변환
        definition_html = markdown.markdown(raw_definition)
        
        # 3. DB에 저장할 때는 순수 텍스트(raw_definition)를 사용
        if 'user' in session:
            try:
                # user_word_history 테이블이 Supabase에 생성되어 있어야 합니다.
                supabase.table('user_word_history').insert({
                    'user_id': session['user']['id'],
                    'word': word,
                    'definition': raw_definition # ◀ 순수 텍스트 저장
                }).execute()
            except Exception as e:
                print(f"Word history logging failed: {e}")

        # 4. 사용자 화면에는 변환된 HTML(definition_html)을 전달
        return jsonify({'word': word, 'definition': definition_html})
        
    except Exception as e:
        print(f"LLM Define API Error: {e}")
        return jsonify({'error': str(e)}), 500
