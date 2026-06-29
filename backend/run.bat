@echo off
chcp 65001 > nul
echo ===================================================
echo [alba-backend] 로컬 개발 서버 실행 스크립트
echo ===================================================

:: 1. .env 파일 확인 및 복사
if not exist .env (
    echo [alba-backend] .env 파일이 없습니다. .env.example을 복사하여 생성합니다...
    copy .env.example .env
    echo [alba-backend] .env 파일이 생성되었습니다. 필요한 경우 설정을 변경해주세요.
)

:: 2. 가상환경 활성화 및 서버 실행
if not exist venv (
    echo [alba-backend] 에러: venv 가상환경이 존재하지 않습니다.
    echo 가상환경을 먼저 생성하고 패키지를 설치해야 합니다.
    pause
    exit /b 1
)

echo [alba-backend] FastAPI 로컬 서버를 포트 8000에서 실행합니다...
echo [alba-backend] Swagger UI 접속 주소: http://localhost:8000/docs
echo ===================================================

.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

pause
