import logging
# pyrefly: ignore [missing-import]
import aiosqlite
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    db_path: str = "alba.db"
    is_connected: bool = False

    @classmethod
    async def connect_db(cls):
        """
        SQLite 데이터베이스 파일 경로를 초기화하고 연결을 테스트합니다.
        데이터베이스 파일에 문제가 있더라도 서버 기동이 멈추지 않도록 예외 처리합니다.
        """
        try:
            # sqlite+aiosqlite:/// 부분 제거하여 파일 경로 추출
            cls.db_path = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
            logger.info(f"SQLite 데이터베이스 경로 설정: {cls.db_path}")
            
            # 테스트 연결 시도
            async with aiosqlite.connect(cls.db_path) as conn:
                await conn.execute("SELECT 1")
            
            cls.is_connected = True
            logger.info("SQLite 데이터베이스 연결 테스트가 완료되었습니다.")
        except Exception as e:
            logger.error(f"SQLite 데이터베이스 파일 연결 테스트 실패 (실시간 프록시로 동작): {e}")
            cls.is_connected = False

    @classmethod
    async def close_db(cls):
        """
        SQLite 연결 종료 로그를 기록합니다 (aiosqlite는 풀을 별도로 관리하지 않고 매번 닫기 때문에 인터페이스 호환용).
        """
        cls.is_connected = False
        logger.info("SQLite 데이터베이스 연결 종료 처리가 완료되었습니다.")

    @classmethod
    async def initialize_db(cls):
        """
        데이터베이스 테이블 및 인덱스를 초기화합니다.
        """
        if not cls.is_connected:
            await cls.connect_db()
            
        if not cls.is_connected:
            logger.warning("데이터베이스가 준비되지 않아 DDL 초기화 단계를 건너뜁니다.")
            return

        # 기존 테이블 스키마 확인 및 마이그레이션
        try:
            async with aiosqlite.connect(cls.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("PRAGMA table_info(crawled_jobs)") as cursor:
                    columns = [row["name"] for row in await cursor.fetchall()]
                
                # 신규 컬럼 중 category가 없으면 구버전 테이블이므로 드롭
                if columns and "category" not in columns:
                    logger.info("구버전 데이터베이스 테이블 감지. 테이블을 재생성합니다...")
                    await conn.execute("DROP TABLE IF EXISTS crawled_jobs;")
                    await conn.commit()
        except Exception as e:
            logger.error(f"테이블 스키마 확인 중 오류 발생: {e}")
            
        ddl = """
        CREATE TABLE IF NOT EXISTS crawled_jobs (
            wanted_auth_no TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            company_name TEXT,
            title TEXT,
            region TEXT,
            pay_info TEXT,
            work_time TEXT,
            register_date TEXT,
            detail_url TEXT,
            category TEXT,
            work_period TEXT,
            work_days TEXT,
            pay_type TEXT,
            pay_amount INTEGER,
            age TEXT,
            conditions TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            async with aiosqlite.connect(cls.db_path) as conn:
                # 테이블 생성
                await conn.execute(ddl)
                # 조회 속도 최적화를 위한 인덱스 생성
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawled_jobs_lookup ON crawled_jobs (company_name, title);")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_crawled_jobs_updated ON crawled_jobs (updated_at DESC);")
                await conn.commit()
                logger.info("SQLite crawled_jobs 테이블 및 인덱스가 성공적으로 초기화되었습니다.")
        except Exception as e:
            logger.error(f"SQLite 테이블 및 인덱스 초기화 중 예외 발생: {e}")

    @classmethod
    async def upsert_jobs(cls, jobs: List[Dict[str, Any]]):
        """
        수집된 채용 공고 데이터를 SQLite에 Upsert 처리합니다.
        """
        if not jobs:
            return
            
        if not cls.is_connected:
            await cls.connect_db()
            
        if not cls.is_connected:
            logger.warning("데이터베이스가 준비되지 않아 수집된 데이터 적재를 생략합니다.")
            return
            
        query = """
        INSERT INTO crawled_jobs (
            wanted_auth_no, source, company_name, title, region, pay_info, work_time, register_date, detail_url,
            category, work_period, work_days, pay_type, pay_amount, age, conditions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (wanted_auth_no)
        DO UPDATE SET
            company_name = EXCLUDED.company_name,
            title = EXCLUDED.title,
            region = EXCLUDED.region,
            pay_info = EXCLUDED.pay_info,
            work_time = EXCLUDED.work_time,
            register_date = EXCLUDED.register_date,
            detail_url = EXCLUDED.detail_url,
            category = EXCLUDED.category,
            work_period = EXCLUDED.work_period,
            work_days = EXCLUDED.work_days,
            pay_type = EXCLUDED.pay_type,
            pay_amount = EXCLUDED.pay_amount,
            age = EXCLUDED.age,
            conditions = EXCLUDED.conditions,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        values = [
            (
                job.get("wanted_auth_no"),
                job.get("source"),
                job.get("company_name"),
                job.get("title"),
                job.get("region"),
                job.get("pay_info"),
                job.get("work_time"),
                job.get("register_date"),
                job.get("detail_url"),
                job.get("category"),
                job.get("work_period"),
                job.get("work_days"),
                job.get("pay_type"),
                job.get("pay_amount"),
                job.get("age"),
                job.get("conditions")
            )
            for job in jobs
        ]
        
        try:
            async with aiosqlite.connect(cls.db_path) as conn:
                await conn.executemany(query, values)
                await conn.commit()
                logger.info(f"SQLite Upsert 성공 - {len(jobs)}개 적재 완료")
        except Exception as e:
            logger.error(f"SQLite Upsert 중 오류 발생: {e}")

    @classmethod
    async def get_jobs(cls, site: str = "all", limit: int = 20) -> List[Dict[str, Any]]:
        """
        DB에 캐싱되어 있는 최신 채용 공고 정보를 조회합니다 (회사명과 제목이 중복되는 경우 최신 1건만 반환).
        데이터베이스 연결 실패 시 빈 리스트를 반환하여 크롤러 폴백을 유도합니다.
        """
        if not cls.is_connected:
            await cls.connect_db()
            
        if not cls.is_connected:
            logger.warning("데이터베이스가 준비되지 않아 캐시 조회 대신 실시간 크롤링으로 진행합니다.")
            return []
            
        site = site.lower().strip()
        
        # 중복 제거를 고려하여 여유있게 가져올 수량 설정 (최소 300개 또는 limit * 4)
        query_limit = max(300, limit * 4)
        
        if site == "all":
            query = """
            SELECT wanted_auth_no, source, company_name, title, region, pay_info, work_time, register_date, detail_url,
                   category, work_period, work_days, pay_type, pay_amount, age, conditions
            FROM crawled_jobs
            ORDER BY updated_at DESC
            LIMIT ?;
            """
            args = [query_limit]
        else:
            query = """
            SELECT wanted_auth_no, source, company_name, title, region, pay_info, work_time, register_date, detail_url,
                   category, work_period, work_days, pay_type, pay_amount, age, conditions
            FROM crawled_jobs
            WHERE LOWER(source) = ?
            ORDER BY updated_at DESC
            LIMIT ?;
            """
            args = [site, query_limit]
            
        try:
            async with aiosqlite.connect(cls.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, args) as cursor:
                    rows = await cursor.fetchall()
                    
                    # Python 레벨에서 회사명 + 제목 기준으로 최신순 중복 제거
                    seen = set()
                    jobs = []
                    for row in rows:
                        company = row["company_name"]
                        title = row["title"]
                        key = (company, title)
                        if key not in seen:
                            seen.add(key)
                            jobs.append({
                                "source": row["source"],
                                "wanted_auth_no": row["wanted_auth_no"],
                                "company_name": company,
                                "title": title,
                                "region": row["region"],
                                "pay_info": row["pay_info"],
                                "work_time": row["work_time"],
                                "register_date": row["register_date"],
                                "detail_url": row["detail_url"],
                                "category": row["category"] or "",
                                "work_period": row["work_period"] or "",
                                "work_days": row["work_days"] or "",
                                "pay_type": row["pay_type"] or "",
                                "pay_amount": row["pay_amount"] or 0,
                                "age": row["age"] or "연령무관",
                                "conditions": row["conditions"] or ""
                            })
                            if len(jobs) >= limit:
                                break
                    return jobs
        except Exception as e:
            logger.error(f"SQLite 데이터 조회 중 오류 발생 (실시간 폴백): {e}")
            return []
