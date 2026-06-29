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
    def parse_pay_amount(pay_str: str) -> int:
        if not pay_str:
            return 0
        nums = re.sub(r'[^0-9]', '', pay_str)
        try:
            return int(nums) if nums else 0
        except ValueError:
            return 0

    @staticmethod
    def extract_time_from_text(text: str) -> Optional[str]:
        if not text:
            return None
        # 1. 09:00~18:00 또는 09:00 - 18:00 형식
        p1 = re.search(r'(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})', text)
        if p1:
            return f"{p1.group(1)}~{p1.group(2)}"
            
        # 2. 23시부터08시까지, 9시~18시, 9시-18시 형식
        p2 = re.search(r'(\d{1,2})\s*시(?:반|\d{2}분)?\s*(?:~|부터|-|내외)\s*(\d{1,2})\s*시(?:반|\d{2}분)?', text)
        if p2:
            matched = p2.group(0).strip()
            # 표준화
            standardized = re.sub(r'\s*(?:~|부터|-|내외)\s*', '~', matched)
            standardized = standardized.rstrip("까지").rstrip("분").strip()
            return standardized
            
        # 3. 5H, 8H 등 시간수 표시
        p3 = re.search(r'(\d{1,2})\s*[hH]\b', text)
        if p3:
            return f"일 {p3.group(1)}시간"
            
        return None

    @staticmethod
    def _parse_alba_heaven_list_html(html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("#NormalInfo tbody tr") or soup.select(".goodsList tbody tr")
        jobs = []
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
                time_el = row.select_one(".time") or row.select_one(".data")
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
            except Exception:
                continue
        return jobs

    @staticmethod
    def _parse_alba_heaven_detail_html(html: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        info = {}
        for term in soup.select(".detail-def__term"):
            desc = term.find_next()
            if desc:
                info[term.get_text(strip=True)] = desc.get_text(strip=True)
        
        category = info.get("모집직종", "")
        work_period = info.get("근무기간", "")
        work_days = info.get("근무요일", "")
        work_time = info.get("근무시간", "")
        age = info.get("학력", "학력무관")
        
        cond_list = []
        for key in ["복리후생", "우대조건", "기타조건"]:
            val = info.get(key, "")
            if val:
                cond_list.append(val)
        conditions = ",".join(cond_list)
        
        return {
            "category": category,
            "work_period": work_period,
            "work_days": work_days,
            "work_time": work_time,
            "age": age,
            "conditions": conditions
        }

    @staticmethod
    def _parse_albamon_list_html(html: str) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(html, "html.parser")
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        if not next_data_script:
            return jobs
            
        js = json.loads(next_data_script.string)
        queries = js.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [])
        if not queries:
            return jobs
            
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
            
            time_str = (item.get("workingTime") or "").strip()
            
            # 알바몬 근무시간이 비어있거나 "협의" 인 경우 제목에서 추출 시도
            if not time_str or "협의" in time_str:
                extracted = AlbaCrawlerService.extract_time_from_text(title)
                if extracted:
                    time_str = extracted
                    
            time_str = time_str or "시간협의"
            reg_date = item.get("postedDate") or ""
            detail_url = f"https://www.albamon.com/jobs/detail/{recruit_no}"
            
            # 직종(category) 가공
            parts = item.get("parts") or []
            category = ",".join(parts) if isinstance(parts, list) else str(parts)
            
            # 복리후생/우대(conditions) 가공
            filter_total = item.get("filterTotal") or ""
            hash_tags = item.get("hashTags") or []
            tags_str = ",".join([t.get("hasTag") for t in hash_tags if t and t.get("hasTag")])
            conditions_list = filter(None, [filter_total, tags_str])
            conditions = ",".join(conditions_list)
            
            parsed_pay_amount = AlbaCrawlerService.parse_pay_amount(item.get("pay", ""))

            jobs.append({
                "source": "Albamon",
                "wanted_auth_no": f"AM_{recruit_no}",
                "company_name": company,
                "title": title,
                "region": region,
                "pay_info": pay,
                "work_time": time_str,
                "register_date": reg_date,
                "detail_url": detail_url,
                "category": category,
                "work_period": item.get("workingPeriod") or "",
                "work_days": item.get("workingWeek") or "",
                "pay_type": pay_type_desc,
                "pay_amount": parsed_pay_amount,
                "age": item.get("age") or "연령무관",
                "conditions": conditions
            })
        return jobs

    @staticmethod
    async def _crawl_alba_heaven_detail(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore) -> Dict[str, Any]:
        if not url:
            return {}
        
        headers = {
            "User-Agent": settings.crawler_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.alba.co.kr/",
        }
        
        async with sem:
            try:
                await asyncio.sleep(0.05)
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                html = response.text
                
                # BeautifulSoup 파싱을 별도 스레드로 위임하여 이벤트 루프 블로킹 방지
                return await asyncio.to_thread(AlbaCrawlerService._parse_alba_heaven_detail_html, html)
            except Exception as e:
                logger.error(f"알바천국 상세 페이지 크롤링 에러 ({url}): {e}")
                return {}

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
            
            # BeautifulSoup 파싱을 별도 스레드로 위임
            jobs = await asyncio.to_thread(AlbaCrawlerService._parse_alba_heaven_list_html, html_content)
            
            # 수집된 jobs들에 대해 상세 페이지 추가 비동기 크롤링 진행
            if jobs:
                sem = asyncio.Semaphore(10)
                tasks = [AlbaCrawlerService._crawl_alba_heaven_detail(client, job["detail_url"], sem) for job in jobs]
                detail_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for job, detail in zip(jobs, detail_results):
                    if isinstance(detail, Exception) or not detail:
                        detail = {}
                    
                    job["category"] = detail.get("category", "")
                    job["work_period"] = detail.get("work_period", "")
                    job["work_days"] = detail.get("work_days", "")
                    job["age"] = detail.get("age", "연령무관")
                    job["conditions"] = detail.get("conditions", "")
                    
                    # 목록에서 빈 값인 경우 상세 페이지 정보로 대체, 둘 다 없으면 "시간협의" 지정
                    db_work_time = job.get("work_time", "").strip()
                    detail_work_time = detail.get("work_time", "").strip()
                    
                    # 우선적으로 상세페이지 근무시간이 "협의"가 아닌 구체적 시간이라면 그것을 적용
                    is_db_negotiable = not db_work_time or "협의" in db_work_time
                    is_detail_specific = detail_work_time and "협의" not in detail_work_time
                    
                    final_work_time = ""
                    if is_db_negotiable and is_detail_specific:
                        final_work_time = detail_work_time
                    else:
                        final_work_time = db_work_time or detail_work_time
                        
                    # 그래도 "협의"이거나 비어있다면, 공고 제목에서 패턴 추출 시도
                    if not final_work_time or "협의" in final_work_time:
                        extracted = AlbaCrawlerService.extract_time_from_text(job.get("title", ""))
                        if extracted:
                            final_work_time = extracted
                            
                    job["work_time"] = final_work_time or "시간협의"
                    
                    # 급여형태 및 급여금액 파싱
                    pay_info = job.get("pay_info", "")
                    pay_type = "시급"
                    if "월급" in pay_info:
                        pay_type = "월급"
                    elif "일급" in pay_info:
                        pay_type = "일급"
                    elif "주급" in pay_info:
                        pay_type = "주급"
                    elif "연봉" in pay_info:
                        pay_type = "연봉"
                    elif "건당" in pay_info:
                        pay_type = "건당"
                    
                    job["pay_type"] = pay_type
                    job["pay_amount"] = AlbaCrawlerService.parse_pay_amount(pay_info)

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
            
            # BeautifulSoup 파싱을 별도 스레드로 위임
            jobs = await asyncio.to_thread(AlbaCrawlerService._parse_albamon_list_html, html_content)
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
        근무시간(work_time)이 비어있거나 "협의"를 포함하는 항목은 제외하고 구체적인 근무시간 정보가 있는 건만 선별합니다.
        """
        site = site.lower().strip()
        tasks = []
        
        # 시간협의가 필터링되므로 4배 더 넉넉하게 긁어옴
        internal_limit = limit * 4
        per_site_limit = internal_limit if site != "all" else max(20, internal_limit // 2)
        
        # 알바천국 상세페이지 대량 조회 시 과도한 네트워크 I/O 및 차단 위험 방지를 위한 안전 제약
        if site == "all":
            # 알바천국은 상세페이지 비동기 조회가 포함되므로 최대 1000개로 수집 제약
            heaven_limit = min(1000, per_site_limit)
            tasks.append(cls.crawl_alba_heaven(limit=heaven_limit))
            tasks.append(cls.crawl_albamon(limit=per_site_limit))
        else:
            if site == "albaheaven":
                tasks.append(cls.crawl_alba_heaven(limit=min(2000, per_site_limit)))
            else:
                tasks.append(cls.crawl_albamon(limit=per_site_limit))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined_jobs = []
        for res in results:
            if isinstance(res, list):
                combined_jobs.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"크롤링 태스크 수행 중 예외 발생: {res}")
                
        # 근무시간이 구체적으로 명시된 데이터만 필터링
        filtered_jobs = []
        for job in combined_jobs:
            wt = job.get("work_time", "").strip()
            # 빈 문자열이거나 "협의" 문구가 들어있으면 배제
            if not wt or "협의" in wt:
                continue
            filtered_jobs.append(job)
            
        filtered_jobs = filtered_jobs[:limit]
        
        return {
            "total": len(filtered_jobs),
            "site": site,
            "jobs": filtered_jobs
        }
