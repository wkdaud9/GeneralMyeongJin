# Dockerfile

# 1. 베이스 이미지 선택
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY requirements.txt requirements.txt
COPY . .

# 4. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. Gunicorn으로 앱 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app