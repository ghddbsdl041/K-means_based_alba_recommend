import logging
import asyncio
from app.services.crawler import AlbaCrawlerService
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

# 동기화 주기 (초 단위 - 30분 = 1800초)
SYNC_INTERVAL_SECONDS = 1800

async def run_sync_task():
    """
    실제 크롤링 후 PostgreSQL 데이터베이스에 데이터를 Upsert 동기화합니다.
    """
    logger.info("실시간 백그라운드 동기화 스케줄 작업 시작...")
    try:
        # 충분한 모수 확보를 위해 2000개씩 크롤링하여 DB 적재
        data = await AlbaCrawlerService.get_combined_jobs(site="all", limit=2000)
        jobs = data.get("jobs", [])
        if jobs:
            await DatabaseManager.upsert_jobs(jobs)
            logger.info(f"실시간 백그라운드 동기화 성공: {len(jobs)}개 적재 완료")
        else:
            logger.warning("동기화할 구인 공고가 발견되지 않았습니다.")
    except Exception as e:
        logger.error(f"백그라운드 동기화 스케줄 작업 중 오류 발생: {e}")

async def start_sync_scheduler():
    """
    FastAPI startup 시 기동될 백그라운드 스케줄러 데몬 루프입니다.
    """
    # 1. 서버 시작 시 초기 딜레이 후 1회 즉시 동기화 실행
    await asyncio.sleep(5)
    await run_sync_task()
    
    # 2. 이후 SYNC_INTERVAL_SECONDS 주기마다 실행
    while True:
        try:
            await asyncio.sleep(SYNC_INTERVAL_SECONDS)
            await run_sync_task()
        except asyncio.CancelledError:
            logger.info("백그라운드 동기화 스케줄러가 종료되었습니다.")
            break
        except Exception as e:
            logger.error(f"스케줄러 루프 예외 발생: {e}")
            await asyncio.sleep(60) # 예외 발생 시 1분 대기 후 재시도
