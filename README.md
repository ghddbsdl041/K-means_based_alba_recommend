# 서울 열린데이터 광장 채용 정보 연동 API Gateway (alba-backend)

서울 열린데이터 광장의 **서울시 일자리포털 채용 정보 오픈API (GetJobInfo)**를 안전하고 신속하게 연동하는 비동기 FastAPI 백엔드 프록시 서버입니다. 

프론트엔드 클라이언트(React, Vue, Next.js 등)에 API Key를 노출하지 않고 안전하게 통신하며, API에서 제공하지 않는 다양한 동적 필터링(키워드 검색, 근무 지역 변환, 알바/시간제 필터, 청년/주니어 필터 등)을 백엔드 메모리상에서 고속으로 수행한 후 응답합니다.

---

## 주요 기능 (Features)

*   **API Key 은닉 (Security)**: 서울 열린데이터 광장 API Key를 프록시 서버 백엔드 내에서만 관리하여 노출을 방지합니다.
*   **고속 비동기 연동 (Performance)**: `httpx` 및 `asyncio.gather`를 사용해 1~2000위까지의 활성 채용 공고 데이터를 비동기 병렬 호출하여 수집합니다.
*   **지능형 필터링 (Intelligent Filtering)**:
    *   **키워드 검색**: 기업명, 모집 직종명, 상세 업무 내용 내 키워드 매칭
    *   **지역 변환 및 필터링**: 기존 고용24 지역 코드(예: `11000`)를 한글 지역명(`서울`, `경기`, `인천`)으로 자동 맵핑하여 지역 조건 검색 지원
    *   **알바/시간제 필터**: 고용 형태 코드(`J01103`, `J01105`) 분석 및 업무명/설명 분석을 통해 시간제/파트타임/아르바이트/일용직만 분류
    *   **청년/주니어 우대 필터**: 신입/경력무관 공고 대상 필터링 및 청년층 비선호 직무(시니어 케어, 청소, 경비, 시설관리 등 단순 노무) 원천 배제
*   **GCP Cloud Run Ready**: 컨테이너화를 통해 손쉬운 인프라 배포가 가능합니다.

---

## 프로젝트 구조 (Project Structure)

```text
alba-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 애플리케이션 초기화, CORS 및 전역 예외 처리
│   ├── config.py            # Pydantic Settings 기반 환경 변수 및 설정 관리
│   ├── core/
│   │   ├── __init__.py
│   │   └── utils.py         # 공통 유틸리티 (XML-to-JSON 파싱 등)
│   ├── services/
│   │   ├── __init__.py
│   │   └── recruitment.py   # 서울 열린데이터 API 연동 및 비동기 수집/필터링 서비스 로직
│   └── routers/
│       ├── __init__.py
│       └── recruitment.py   # /api/recruitment 관련 API 라우터/엔드포인트
├── .dockerignore            # Docker 빌드 제외 설정
├── .env                     # 로컬 실행 환경 변수 정의 (Git 관리 대상 제외)
├── .env.example             # 환경 변수 구성 가이드 템플릿
├── Dockerfile               # Production 배포용 Docker 설정 파일 (Python 3.11-slim)
├── deploy.sh                # GCP Cloud Run 자동 배포 스크립트
├── requirements.txt         # 파이썬 패키지 의존성 정의
└── README.md
```

---

## 환경 설정 및 실행 방법 (Setup & Running)

### 1. 요구 사항
*   **Python 3.9 이상** (Docker 실행 시 Python 3.11 이미지 사용)

### 2. 가상환경 구축 및 패키지 설치
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 구성
프로젝트 루트 폴더에 `.env` 파일을 생성하거나 `.env.example` 파일을 복사하여 실키(API Key)를 기입합니다.
```env
# 서울 열린데이터 광장 API 인증키
SEOUL_OPEN_DATA_API_KEY=your_seoul_open_data_api_key_here

# 서버 구성
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 4. 로컬 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```
서버 실행 후 **[http://localhost:8000/docs](http://localhost:8000/docs)**에 접속하면 대화형 Swagger API 문서를 확인하고 테스트할 수 있습니다.

---

## API 엔드포인트 정의 (API Endpoints)

### 1. 채용 정보 검색 및 목록 조회
*   **`GET /api/recruitment/jobs`**
    *   **설명**: 서울 열린데이터 광장의 실시간 채용 정보 목록을 조회합니다. 필터 조건이 주어질 경우 메모리 내 고성능 필터링을 가동합니다.
    *   **주요 쿼리 파라미터**:
        *   `keyword` (Optional): 검색 키워드 (예: `개발자`, `쿠팡`, `바리스타`)
        *   `region` (Optional): 지역/자치구 이름 또는 고용24 지역 코드 (예: `강남구`, `11000` -> `서울`로 자동 매핑)
        *   `occupation` (Optional): 모집 직종 코드 또는 직무명
        *   `is_part_time` (Optional): `true` 설정 시 알바/시간제 채용 정보만 필터링
        *   `is_youth` (Optional): `true` 설정 시 청년/주니어 적합 채용 정보만 필터링 (신입, 경력 무관, 청년 우대 및 단순 노무 업종 배제)
        *   `start_page` (Optional): 조회할 페이지 번호 (기본값: `1`)
        *   `display` (Optional): 페이지당 출력할 공고 개수 (기본값: `10`, 최대: `500`)

### 2. 채용 상세 정보 조회
*   **`GET /api/recruitment/jobs/{wanted_auth_no}`**
    *   **설명**: 구인신청번호(`JO_REQST_NO`)를 기반으로 특정 구인 공고의 상세 요강 정보를 조회합니다.
    *   **경로 파라미터**:
        *   `wanted_auth_no`: 구인신청번호 (예: `JO_REQST_NO` 문자열)
    *   **예외 처리**: 활성 채용 목록 풀에 없거나 상세 정보가 만료된 공고의 경우, 연동 오류를 방지하기 위해 가짜 스텁 데이터(Fallback Stub)를 반환합니다.

---

## 빌드 및 배포 (Build & Deploy)

### Docker 빌드 및 로컬 실행
```bash
# Docker 이미지 빌드
docker build -t alba-backend:latest .

# 컨테이너 실행 (로컬 8080 포트 포워딩)
docker run -p 8080:8080 --env-file .env alba-backend:latest
```

### GCP Cloud Run 배포
`deploy.sh` 스크립트를 통해 Google Cloud Run에 손쉽게 배포할 수 있습니다.
```bash
chmod +x deploy.sh
./deploy.sh
```
*   **배포 리전**: `us-central1`
*   **배포 서비스명**: `alba-backend`
*   **자동 환경 변수**: 배포 스크립트에 운영 환경용 `SEOUL_OPEN_DATA_API_KEY`와 `DEBUG=False` 설정이 내장되어 주입됩니다.
*   **인스턴스 설정**: 콜드 스타트 지연 방지를 위해 상시 기동 인스턴스를 최소 1개 유지하도록 구성되어 있습니다 (`--min-instances=1`).
