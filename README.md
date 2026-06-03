# 알바몬 & 알바천국 서울 아르바이트 통합 캐시 API Gateway (alba-backend)

알바몬(Albamon)과 알바천국(AlbaHeaven)의 서울 전체 지역 일반 아르바이트 채용 정보를 비동기 병렬로 크롤링하여 **비동기 SQLite 데이터베이스(`aiosqlite`)**에 캐싱한 후, 프론트엔드에 대기 시간 없이 초고속(0.3초대)으로 데이터를 반환해 주는 API 게이트웨이 백엔드 서버입니다.

웹 스크래핑 시 필연적으로 발생하는 수 초~수십 초의 대기 지연을 없애고, **물리적인 DB 캐시 조회와 백그라운드 삼중 동기화 아키텍처**를 결합하여 안정성과 반응성을 극대화했습니다.

---

## 🚀 주요 기능 (Features)

*   **비동기 다중 페이지 병렬 크롤링 (Crawling)**:
    *   `asyncio.gather` 및 `httpx`를 사용하여 알바몬(Next.js `__NEXT_DATA__` JSON 파싱)과 알바천국(WAF 우회 모바일 엔드포인트)에서 최대 2000개의 구인 데이터를 고속으로 병렬 수집합니다.
*   **비동기 SQLite 캐싱 (`aiosqlite`)**:
    *   I/O 블로킹을 방지하기 위해 비동기 SQLite 라이브러리인 `aiosqlite`를 연동하여 로컬 디스크 파일(`alba.db`)에 데이터를 안전하게 영속화합니다.
*   **삼중 자동 동기화 시스템**:
    1.  **초기 기동 동기화**: 서버 시작 5초 후 자동으로 1회 즉시 크롤링을 수행하여 DB를 초기화합니다.
    2.  **30분 주기 스케줄링**: 백그라운드 데몬이 30분(1800초) 주기로 2000개 수집 크롤러를 가동해 캐시를 갱신합니다.
    3.  **API 호출 트리거 갱신**: 사용자가 API를 호출하면 DB 캐시 데이터를 1ms 이내로 즉시 쏴주고, 동시에 백그라운드 태스크(`BackgroundTasks`)로 최신 데이터를 업데이트합니다.
*   **논리적 중복 필터링 및 쿼리 최적화**:
    *   동일한 회사명(`company_name`)과 제목(`title`)의 구인 공고가 ID만 다르게 중복 등록된 경우, 가장 최근의 공고 1개만 남기고 필터링하여 사용자에게 서빙합니다.
    *   데이터가 대량 적재(2,700여 개 이상)된 환경에서도 정렬 및 중복 제어로 인한 지연이 발생하지 않도록 **복합 인덱스 `(company_name, title)` 및 `(updated_at DESC)`**를 DDL 기동 시 자동 빌드하도록 튜닝하여 **API 응답 속도를 0.3초대(380ms)로 최적화**했습니다.

---

## 📂 프로젝트 구조 (Project Structure)

```text
alba-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 인스턴스, 수명 주기 이벤트(DB 연결 및 스케줄러 기동) 관리
│   ├── config.py            # Pydantic Settings 기반 환경 변수 및 설정
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py      # aiosqlite 기반 테이블/인덱스 생성 DDL, Upsert 및 최적화 중복제거 조회
│   │   ├── scheduler.py     # 30분 주기 백그라운드 동기화 스케줄러 데몬
│   │   └── utils.py         # 공통 유틸리티
│   ├── services/
│   │   ├── __init__.py
│   │   └── crawler.py       # 알바몬 Next.js 데이터 파싱 및 알바천국 병렬 스크래핑 엔진
│   └── routers/
│       ├── __init__.py
│       └── recruitment.py   # /crawled-jobs API 라우터 정의 (BackgroundTasks 연동)
├── .dockerignore
├── .env                     # 로컬 실행 환경 변수 (sqlite 주소 포함)
├── .env.example
├── Dockerfile               # Production 배포용 Docker 설정 (Python 3.11-slim)
├── deploy.sh                # GCP Cloud Run 자동 배포 스크립트
├── requirements.txt         # 파이썬 패키지 의존성 (aiosqlite 포함)
└── README.md
```

---

## 🛠 환경 설정 및 실행 방법 (Setup & Running)

### 1. 요구 사항
*   **Python 3.9 이상** (가상환경 venv 내 실행 권장)

### 2. 패키지 설치
```bash
# 가상환경 활성화 후 실행
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 변수 구성 (`.env`)
루트 폴더에 `.env` 파일을 복사/생성하여 아래 설정을 기입합니다.
```env
SEOUL_OPEN_DATA_API_KEY=724b6d48746b646837324259507a7a
HOST=0.0.0.0
PORT=8000
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///alba.db
```

### 4. 로컬 서버 실행
```bash
uvicorn app.main:app --reload --port 8000
```
서버 실행 후 **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)에 접속하여 API를 즉시 테스트해볼 수 있습니다.

---

## 🔌 API 엔드포인트 정의 (API Endpoints)

### 1. 크롤링 채용 정보 캐시 조회
*   **`GET /api/recruitment/crawled-jobs`**
*   **쿼리 파라미터**:
    *   `site` (Optional, 기본값 `all`): 조회할 대상 사이트 (`all`, `albamon`, `albaheaven`)
    *   `limit` (Optional, 기본값 `50`, 최대 `2000`): 최대로 가져올 구인 공고 개수
    *   `force_refresh` (Optional, 기본값 `false`): `true` 설정 시 DB 캐시 조회를 생략하고 즉시 대량 크롤링을 직접 수행하여 DB를 강제 갱신한 후 결과를 반환합니다 (약 5~15초 소요).
*   **동작 매커니즘**:
    *   `force_refresh=false`인 경우: SQLite DB에서 회사명/제목 기준 중복이 배제된 캐시 데이터를 **즉시 응답**합니다. 이와 동시에 비동기 `BackgroundTasks`가 돌아 최신 2000개의 데이터를 크롤링하여 DB 캐시를 갱신합니다.

---

## 🚀 빌드 및 배포 (Build & Deploy)

### Docker 로컬 빌드 및 실행
```bash
# Docker 이미지 빌드
docker build -t alba-backend:latest .

# 컨테이너 실행
docker run -p 8080:8080 --env-file .env alba-backend:latest
```

### GCP Cloud Run 배포
수정된 배포 환경에 맞춰 작성된 `deploy.sh` 스크립트를 통해 Cloud Run 단독 배포를 손쉽게 진행할 수 있습니다.
```bash
chmod +x deploy.sh
./deploy.sh
```
*   **배포 리전**: `us-central1`
*   **배포 프로젝트**: `ounse-booth-2026`
*   **환경변수**: 컨테이너 구동 시 `DATABASE_URL=sqlite+aiosqlite:///alba.db`가 자동으로 주입되어 컨테이너 인스턴스 내부의 로컬 디스크를 활용해 SQLite 캐싱을 처리합니다.
*   **알림 (컨테이너 휘발성 제약)**: Cloud Run 인스턴스가 다운되거나 재배포될 경우 내부 `alba.db` 파일이 휘발됩니다. 하지만 본 서비스는 기동과 동시에 최초 1회 전체 동기화를 실행하고 30분 주기 스케줄링 및 API 호출 시 비동기 업데이트가 돌기 때문에, 유실 시 즉시 자동 복구되어 정상 서빙을 유지합니다.
