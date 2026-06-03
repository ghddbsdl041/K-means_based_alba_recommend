import logging
import json
import asyncio
import re
import math
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AlbaCrawlerService:
    @staticmethod
    async def crawl_alba_heaven_page(client: httpx.AsyncClient, page: int) -> List[Dict[str, Any]]:
        """
        알바천국 특정 페이지의 서울 알바 채용공고를 단일 요청하여 수집합니다.
        """
        url = f"https://www.alba.co.kr/job/area/ColledgeList.asp?sidocd=02&page={page}"
        headers = {
            "User-Agent": settings.crawler_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.alba.co.kr/",
        }
        
        jobs = []
        try:
            logger.info(f"알바천국 단일 페이지 호출 (Page: {page})")
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            html_content = response.text
            
            soup = BeautifulSoup(html_content, "html.parser")
            rows = soup.select("#NormalInfo tbody tr") or soup.select(".goodsList tbody tr")
            
            for row in rows:
                if "summary" in row.get("class", []) or "gSub" in row.get("class", []):
                    continue
                
                try:
                    # 1. 회사명
                    company_el = row.select_one(".company")
                    if not company_el:
                        continue
                    company = company_el.get_text(strip=True)
                    
                    # 2. 제목 및 링크
                    title_el = row.select_one(".title a") or row.select_one("a.goodsTitle") or row.select_one(".title")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    title = re.sub(r'\s+', ' ', title)
                    
                    link = ""
                    if title_el.name == "a" and title_el.get("href"):
                        href = title_el.get("href")
                        if href.startswith("http"):
                            link = href
                        else:
                            link = f"https://www.alba.co.kr{href}"
                    
                    # 3. 근무지
                    local_el = row.select_one(".local")
                    local = local_el.get_text(strip=True) if local_el else ""
                    
                    # 서울 지역 검증
                    if "서울" not in local:
                        continue
                    
                    # 4. 급여
                    pay_el = row.select_one(".pay")
                    pay = pay_el.get_text(strip=True) if pay_el else ""
                    pay = re.sub(r'\s+', ' ', pay)
                    
                    # 5. 근무시간
                    time_el = row.select_one(".time")
                    time_str = time_el.get_text(strip=True) if time_el else ""
                    
                    # 6. 등록일
                    reg_date_el = row.select_one(".regDate") or row.select_one(".date")
                    reg_date = reg_date_el.get_text(strip=True) if reg_date_el else ""
                    
                    wanted_auth_no = ""
                    if link:
                        match = re.search(r'adid=(\d+)', link) or re.search(r'(\d+)', link)
                        if match:
                            wanted_auth_no = f"AH_{match.group(1)}"
                    
                    if not wanted_auth_no:
                        import uuid
                        wanted_auth_no = f"AH_{uuid.uuid4().hex[:8]}"

                    jobs.append({
                        "source": "AlbaHeaven",
                        "wanted_auth_no": wanted_auth_no,
                        "company_name": company,
                        "title": title,
                        "region": local,
                        "pay_info": pay,
                        "work_time": time_str,
                        "register_date": reg_date,
                        "detail_url": link
                    })
                except Exception as row_err:
                    continue
        except Exception as e:
            logger.error(f"알바천국 Page {page} 크롤링 실패: {e}")
            
        return jobs

    @staticmethod
    async def crawl_alba_heaven(limit: int = 20) -> List[Dict[str, Any]]:
        """
        요청된 limit 개수를 채우기 위해 여러 페이지를 비동기 병렬로 한꺼번에 긁어모아 반환합니다.
        """
        # 알바천국은 한 페이지당 평균 40~50개의 서울 지역 알바를 수집할 수 있음
        estimated_pages = max(1, math.ceil(limit / 40))
        # 과도한 요청 방지를 위해 병렬 수집 페이지 상한 설정 (최대 60페이지)
        pages_to_crawl = min(60, estimated_pages)
        
        logger.info(f"알바천국 전체 수집 가동 - 목표 수량: {limit}, 동시 크롤링 페이지 수: {pages_to_crawl}")
        
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            tasks = [AlbaCrawlerService.crawl_alba_heaven_page(client, page) for page in range(1, pages_to_crawl + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        jobs = []
        seen_auth_nos = set()
        
        for res in results:
            if isinstance(res, list):
                for job in res:
                    auth_no = job.get("wanted_auth_no")
                    if auth_no not in seen_auth_nos:
                        seen_auth_nos.add(auth_no)
                        jobs.append(job)
                        
        logger.info(f"알바천국 누적 필터링 완료 - 총 {len(jobs)}개 수집됨")
        return jobs[:limit]

    @staticmethod
    async def crawl_albamon_page(client: httpx.AsyncClient, page: int) -> List[Dict[str, Any]]:
        """
        알바몬 특정 페이지의 서울 알바 채용공고를 단일 요청하여 수집합니다.
        """
        url = f"https://m.albamon.com/jobs/area?area=I000&page={page}"
        headers = {
            "User-Agent": settings.crawler_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        jobs = []
        try:
            logger.info(f"알바몬 단일 페이지 호출 (Page: {page})")
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            html_content = response.text
            
            soup = BeautifulSoup(html_content, "html.parser")
            next_data_script = soup.find("script", id="__NEXT_DATA__")
            
            if next_data_script:
                js = json.loads(next_data_script.string)
                queries = js.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
                
                if queries:
                    state_data = queries[0].get("state", {}).get("data", {})
                    base = state_data.get("base", {})
                    paid = state_data.get("paid", {})
                    
                    collections_to_search = []
                    # base 섹션 수집
                    for key in ["normal", "mobileTop", "mobileTopPlus", "mobileTopLogo"]:
                        section = base.get(key, {})
                        if isinstance(section, dict):
                            coll = section.get("collection")
                            if isinstance(coll, list):
                                collections_to_search.extend(coll)
                                
                    # paid 섹션 수집
                    for key in ["mobileTopBanner", "mobileBanner", "pcFranchiseBox", "pcGrand", "pcGrandGold"]:
                        section = paid.get(key, {})
                        if isinstance(section, dict):
                            coll = section.get("collection")
                            if isinstance(coll, list):
                                collections_to_search.extend(coll)
                                
                    for item in collections_to_search:
                        recruit_no = item.get("recruitNo")
                        company = item.get("companyName")
                        title = item.get("recruitTitle")
                        
                        if not company or not title or not recruit_no:
                            continue
                            
                        region = item.get("workplaceArea") or item.get("workplaceAddress") or ""
                        if "서울" not in region:
                            continue
                            
                        pay_type_desc = item.get("payType", {}).get("description", "")
                        pay_amount = item.get("pay", "")
                        pay = f"{pay_type_desc} {pay_amount}".strip()
                        
                        time_str = item.get("workingTime") or ""
                        reg_date = item.get("postedDate") or ""
                        detail_url = f"https://www.albamon.com/recruitment/detail/{recruit_no}"
                        
                        jobs.append({
                            "source": "Albamon",
                            "wanted_auth_no": f"AM_{recruit_no}",
                            "company_name": company,
                            "title": title,
                            "region": region,
                            "pay_info": pay,
                            "work_time": time_str,
                            "register_date": reg_date,
                            "detail_url": detail_url
                        })
        except Exception as e:
            logger.error(f"알바몬 Page {page} 크롤링 실패: {e}")
            
        return jobs

    @staticmethod
    async def crawl_albamon(limit: int = 20) -> List[Dict[str, Any]]:
        """
        요청된 limit 개수를 채우기 위해 여러 페이지를 비동기 병렬로 한꺼번에 긁어모아 반환합니다.
        """
        # 알바몬은 한 페이지당 평균 15~20개의 서울 지역 알바를 수집할 수 있음
        estimated_pages = max(1, math.ceil(limit / 15))
        # 과도한 요청 방지를 위해 병렬 수집 페이지 상한 설정 (최대 150페이지)
        pages_to_crawl = min(150, estimated_pages)
        
        logger.info(f"알바몬 전체 수집 가동 - 목표 수량: {limit}, 동시 크롤링 페이지 수: {pages_to_crawl}")
        
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            tasks = [AlbaCrawlerService.crawl_albamon_page(client, page) for page in range(1, pages_to_crawl + 1)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        jobs = []
        seen_auth_nos = set()
        
        for res in results:
            if isinstance(res, list):
                for job in res:
                    auth_no = job.get("wanted_auth_no")
                    if auth_no not in seen_auth_nos:
                        seen_auth_nos.add(auth_no)
                        jobs.append(job)
                        
        logger.info(f"알바몬 누적 필터링 완료 - 총 {len(jobs)}개 수집됨")
        return jobs[:limit]

    @classmethod
    async def get_combined_jobs(cls, site: str = "all", limit: int = 20) -> Dict[str, Any]:
        """
        알바몬과 알바천국의 크롤링 결과를 수집하고 병합하여 표준화된 형태로 반환합니다.
        """
        site = site.lower().strip()
        tasks = []
        
        per_site_limit = limit if site != "all" else max(10, limit // 2)
        
        if site in ("all", "albaheaven"):
            tasks.append(cls.crawl_alba_heaven(limit=per_site_limit))
        if site in ("all", "albamon"):
            tasks.append(cls.crawl_albamon(limit=per_site_limit))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined_jobs = []
        for res in results:
            if isinstance(res, list):
                combined_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"크롤링 태스크 수행 중 예외 발생: {res}")
                
        combined_jobs = combined_jobs[:limit]
        
        return {
            "total": len(combined_jobs),
            "site": site,
            "jobs": combined_jobs
        }
