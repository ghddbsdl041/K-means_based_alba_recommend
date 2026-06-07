import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from app.services.crawler import AlbaCrawlerService
from app.services.preprocessing import PreprocessingService
from app.core.database import DatabaseManager


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recruitment", tags=["Recruitment"])

async def background_sync_jobs(site: str, limit: int):
    try:
        data = await AlbaCrawlerService.get_combined_jobs(site=site, limit=limit)
        jobs = data.get("jobs", [])
        if jobs:
            await DatabaseManager.upsert_jobs(jobs)
    except Exception as e:
        logger.error(f"백그라운드 API 트리거 동기화 중 예외 발생: {e}")

@router.get("/crawled-jobs", summary="Get crawled job openings from Albamon and Alba Heaven")
async def get_crawled_jobs(
    background_tasks: BackgroundTasks,
    site: str = Query("all", description="크롤링할 대상 사이트 (all, albamon, albaheaven)"),
    limit: int = Query(50, ge=1, le=2000, description="최대 조회 공고 개수 (최대 2000)"),
    force_refresh: bool = Query(False, description="True 설정 시 DB 캐시를 거치지 않고 실시간 크롤링을 수행하여 DB를 강제 갱신한 뒤 즉시 반환합니다.")
):
    """
    알바몬 및 알바천국의 서울 지역 전체 아르바이트 채용 공고 데이터를 실시간/캐시 방식으로 가져옵니다.
    - force_refresh=False (기본값): DB에 저장된 캐시 목록을 1ms 내외로 초고속 반환하고, 동시에 백그라운드로 최신 데이터를 긁어와 DB를 실시간 갱신합니다.
    - force_refresh=True: 실시간으로 직접 대량 크롤링을 대기하여 가져온 뒤 DB를 강제 갱신(Upsert)하고 그 결과를 리턴합니다.
    """
    if site not in ("all", "albamon", "albaheaven"):
        raise HTTPException(status_code=400, detail="site 파라미터는 'all', 'albamon', 'albaheaven' 중 하나여야 합니다.")
        
    try:
        # 1. 강제 실시간 크롤링 및 DB 갱신
        if force_refresh:
            data = await AlbaCrawlerService.get_combined_jobs(site=site, limit=limit)
            jobs = data.get("jobs", [])
            if jobs:
                await DatabaseManager.upsert_jobs(jobs)
            return data
            
        # 2. DB 캐시 데이터 조회 및 즉시 반환 (동기식 실시간 크롤링 폴백 원천 제거)
        cached_jobs = await DatabaseManager.get_jobs(site=site, limit=limit)
        
        # 만약 DB 캐시가 완전히 비어있을 때만, 클라이언트를 대기시키지 않고 백그라운드 태스크로 동기화를 유도
        if not cached_jobs:
            logger.info("DB 캐시가 비어있습니다. 백그라운드에서 크롤링 동기화를 개시합니다.")
            sync_limit = max(400, limit)
            background_tasks.add_task(background_sync_jobs, site, sync_limit)
            
        return {
            "total": len(cached_jobs),
            "site": site,
            "jobs": cached_jobs
        }

    except Exception as e:
        logger.error(f"get_crawled_jobs 엔드포인트 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preprocessed-jobs", summary="Get preprocessed job data for clustering")
async def get_preprocessed_jobs(
    limit: int = Query(50, ge=1, le=2000, description="최대 조회 공고 개수")
):
    """
    수집된 공고 데이터를 클러스터링하기 위해 사진에 정의된 전처리 로직(피처 추출)을 거친 데이터를 확인하는 API입니다.
    """
    try:
        # 1. DB에서 캐시된 데이터 가져오기 (가장 빠른 방법)
        cached_jobs = await DatabaseManager.get_jobs(site="all", limit=limit)
        
        if not cached_jobs:
            # DB에 없으면 크롤링
            data = await AlbaCrawlerService.get_combined_jobs(site="all", limit=limit)
            cached_jobs = data.get("jobs", [])
            
        # 2. 전처리 진행
        preprocessed_data = PreprocessingService.preprocess_jobs(cached_jobs)
        
        return {
            "total": len(preprocessed_data),
            "data": preprocessed_data
        }
    except Exception as e:
        logger.error(f"get_preprocessed_jobs 엔드포인트 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
