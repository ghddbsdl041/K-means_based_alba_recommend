import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import recruitment

# 기본적인 로깅 형식 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="서울 열린데이터 광장 채용 정보 연동 API Gateway",
    description="서울시 일자리포털 채용 정보 오픈API를 안전하고 신속하게 연동하는 비동기 FastAPI 백엔드 프록시 서버입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# React, Vue, Next.js 등 프론트엔드 웹 어플리케이션 요청을 허용하기 위한 CORS 미들웨어 구성
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 서버 환경에서는 보안 강화를 위해 특정 도메인으로 제한하는 것을 권장합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 처리되지 않은 예외를 포착하여 깔끔한 JSON 응답으로 반환하는 전역 예외 처리기
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected server error occurred: {str(exc)}"}
    )

# API 라우터 등록
app.include_router(recruitment.router)

@app.get("/", tags=["Root"])
async def root():
    """
    헬스체크 및 백엔드 API 메타데이터 정보 조회.
    """
    return {
        "status": "healthy",
        "service": "Seoul Open Data API Gateway",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
