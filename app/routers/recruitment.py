import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
from app.services.crawler import AlbaCrawlerService
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
            
        # 2. DB 캐시 데이터 조회
        cached_jobs = await DatabaseManager.get_jobs(site=site, limit=limit)
        
        # 3. DB에 캐시 데이터가 존재하는 경우 (초고속 반환 및 백그라운드 갱신)
        if cached_jobs:
            sync_limit = max(2000, limit)
            background_tasks.add_task(background_sync_jobs, site, sync_limit)
            return {
                "total": len(cached_jobs),
                "site": site,
                "jobs": cached_jobs
            }
            
        # 4. DB 캐시 데이터가 전혀 없거나 DB 연결 실패한 경우 (실시간 크롤링으로 폴백)
        logger.info("DB 캐시 데이터가 없거나 연결할 수 없습니다. 실시간 크롤링으로 응답합니다.")
        data = await AlbaCrawlerService.get_combined_jobs(site=site, limit=limit)
        jobs = data.get("jobs", [])
        if jobs:
            background_tasks.add_task(DatabaseManager.upsert_jobs, jobs)
        return data

    except Exception as e:
        logger.error(f"get_crawled_jobs 엔드포인트 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
