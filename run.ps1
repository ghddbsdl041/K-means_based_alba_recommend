# Force UTF-8 output
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "[alba-backend] 로컬 개발 서버 실행 스크립트" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# 1. .env 파일 확인 및 복사
if (-not (Test-Path ".env")) {
    Write-Host "[alba-backend] .env 파일이 없습니다. .env.example을 복사하여 생성합니다..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[alba-backend] .env 파일이 생성되었습니다. 필요한 경우 설정을 변경해주세요." -ForegroundColor Green
}

# 2. 가상환경 확인
if (-not (Test-Path "venv")) {
    Write-Host "[alba-backend] 에러: venv 가상환경이 존재하지 않습니다." -ForegroundColor Red
    Write-Host "가상환경을 먼저 생성하고 패키지를 설치해야 합니다." -ForegroundColor Red
    Read-Host "종료하려면 Enter 키를 누르세요..."
    exit 1
}

Write-Host "[alba-backend] FastAPI 로컬 서버를 포트 8000에서 실행합니다..." -ForegroundColor Green
Write-Host "[alba-backend] Swagger UI 접속 주소: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

& .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
