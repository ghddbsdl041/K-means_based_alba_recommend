# Python 3.11-slim 프로덕션 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 환경 변수 설정 (바이트코드 생성 금지, 버퍼링 없는 스트림)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 빌드 및 시스템 의존성 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 8080 포트 컨테이너 개방
EXPOSE 8080

# Cloud Run에서 제공하는 PORT 환경 변수를 바인딩하여 FastAPI 구동
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
