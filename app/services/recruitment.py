import logging
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger(__name__)

class RecruitmentService:
    @staticmethod
    async def get_job_openings(
        keyword: Optional[str] = None,
        region: Optional[str] = None,
        occupation: Optional[str] = None,
        is_part_time: Optional[bool] = None,
        is_youth: Optional[bool] = None,
        start_page: int = 1,
        display: int = 10,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        서울 열린데이터 광장의 GetJobInfo(서울시 일자리포털 채용 정보) API로부터 활성화된 채용 공고 목록을 가져옵니다.
        검색 키워드나 기타 필터(알바, 청년 등)가 활성화되어 있으면, 대량의 최근 데이터를 먼저 로드한 뒤 Python 메모리상에서 고속 필터링을 수행합니다.
        필터가 지정되지 않은 경우, 요청받은 페이지와 개수에 해당하는 인덱스 범위를 상용 API로 직접 호출해 반환합니다.
        """
        # 기존 고용24/워크넷 지역 코드를 서울 열린데이터 API 호환이 가능한 한글 주소 문자열로 자동 매칭 및 변환합니다.
        if region:
            region_str = str(region).strip()
            if region_str.isdigit():
                if region_str.startswith("11"): # 서울 지역 코드
                    region = "서울"
                elif region_str.startswith("41"): # 경기 지역 코드
                    region = "경기"
                elif region_str.startswith("28"): # 인천 지역 코드
                    region = "인천"
            elif region_str in ("11000", "11"):
                region = "서울"

        logger.info(f"get_job_openings 호출 매개변수 분석 완료 - keyword: {keyword}, region: {region}, occupation: {occupation}, is_part_time: {is_part_time}, is_youth: {is_youth}, extra_params: {extra_params}")

        # 지연 필터(키워드, 지역, 직종, 알바, 청년) 중 하나라도 활성화된 경우 대량 필터링 필요
        needs_filtering = bool(keyword or region or occupation or is_part_time or is_youth)
        
        rows = []
        total_count = 0

        # API URL 생성 도우미 함수 정의 (선택적 필터 파라미터 순서 준수)
        import urllib.parse
        def build_url(start: int, end: int, r_filter: Optional[str] = None) -> str:
            # 1. 학력코드 (공백)
            # 2. 고용형태코드 (공백)
            # 3. 근무예정지 주소 (region)
            # 4. 경력조건코드 (공백)
            # 5. 등록일 (공백)
            acdmcr_q = urllib.parse.quote(" ")
            emplym_q = urllib.parse.quote(" ")
            region_q = urllib.parse.quote(r_filter) if r_filter else urllib.parse.quote(" ")
            career_q = urllib.parse.quote(" ")
            
            return f"{settings.seoul_open_data_base_url}/{settings.seoul_open_data_api_key}/json/GetJobInfo/{start}/{end}/{acdmcr_q}/{emplym_q}/{region_q}/{career_q}/"

        if needs_filtering:
            # 2000개의 대량 데이터를 가져오기 위해 2개의 요청을 비동기 병렬 호출하여 병합합니다.
            # 지역 필터가 있다면 API 호출 경로 자체에 지역을 전달하여 1차적으로 고효율 지역 필터링을 거칩니다.
            url1 = build_url(1, 1000, region)
            url2 = build_url(1001, 2000, region)
            
            logger.info(f"서울 열린데이터 API 대량 연동 호출 중 (1-2000) - 지역 필터 적용: {region}")
            
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    res1, res2 = await asyncio.gather(
                        client.get(url1),
                        client.get(url2)
                    )
                
                # 1차 배치 파싱 (1-1000)
                if res1.status_code == 200:
                    d1 = res1.json()
                    if "RESULT" in d1:
                        code = d1["RESULT"].get("CODE")
                        msg = d1["RESULT"].get("MESSAGE", "Unknown API error")
                        if code != "INFO-200":  # INFO-200은 검색 결과가 아예 없는 정상 케이스
                            logger.error(f"Seoul Open Data API 1차 배치 오류: {code} - {msg}")
                    elif "GetJobInfo" in d1:
                        rows.extend(d1["GetJobInfo"].get("row", []))
                        total_count = int(d1["GetJobInfo"].get("list_total_count", 0))
                        
                # 2차 배치 파싱 (1001-2000)
                if res2.status_code == 200:
                    d2 = res2.json()
                    if "GetJobInfo" in d2 and "row" in d2["GetJobInfo"]:
                        rows.extend(d2["GetJobInfo"].get("row", []))
                        
            except Exception as e:
                logger.error(f"비동기 대량 채용 데이터 수집 실패: {e}")
                raise RuntimeError(f"서울 열린데이터 API 통신 중 에러 발생: {str(e)}")
        else:
            # 필터가 없을 시 지정된 페이지 범위에 맞춘 인덱스 직접 대조 방식 설정
            start_idx = (start_page - 1) * display + 1
            end_idx = start_page * display
            url = build_url(start_idx, end_idx)
            
            logger.info(f"서울 열린데이터 API 연동 호출 중: {start_idx} ~ {end_idx}")
            
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # API 인증키 오류나 유효하지 않은 요청 등 공통 에러 응답 분기 처리
                    if "RESULT" in data:
                        code = data["RESULT"].get("CODE")
                        msg = data["RESULT"].get("MESSAGE", "Unknown API error")
                        if code != "INFO-200":
                            logger.error(f"Seoul Open Data API error: {code} - {msg}")
                            raise RuntimeError(f"Seoul Open Data API error: {msg} ({code})")
                    
                    if "GetJobInfo" in data:
                        job_info = data["GetJobInfo"]
                        total_count = int(job_info.get("list_total_count", 0))
                        rows = job_info.get("row", [])
            except Exception as e:
                logger.error(f"Failed to fetch direct recruitment data: {e}")
                raise RuntimeError(f"Failed to communicate with Seoul Open Data API: {str(e)}")

        # 대량 데이터를 가져왔을 때 메모리 상에서 세부 필터링 및 페이징 적용
        if needs_filtering:
            filtered_rows = []
            for row in rows:
                match = True
                
                # 1. 키워드 필터링
                if keyword:
                    k = keyword.lower()
                    company = str(row.get("CMPNY_NM", "")).lower()
                    job_title = str(row.get("JOBCODE_NM", "")).lower()
                    job_desc = str(row.get("DTY_CN", "")).lower()
                    # 기업명, 모집 직종 타이틀, 또는 상세 구인요강 본문 내에 검색 키워드가 매칭되는지 분석
                    if k not in company and k not in job_title and k not in job_desc:
                        match = False
                
                # 2. 지역 필터링 (API 1차 필터의 2차 정밀 확인)
                if region and match:
                    r = region.lower()
                    address = str(row.get("WORK_PARAR_BASS_ADRES_CN", "")).lower()
                    if r not in address:
                        match = False
                        
                # 3. 직종 필터링
                if occupation and match:
                    occ = occupation.lower()
                    occ_code = str(row.get("RCRIT_JSSFC_CMMN_CODE_SE", "")).lower()
                    occ_name = str(row.get("JOBCODE_NM", "")).lower()
                    if occ not in occ_code and occ not in occ_name:
                        match = False

                # 4. 알바/시간제 필터링
                if is_part_time and match:
                    emp_code = str(row.get("EMPLYM_STLE_CMMN_CODE_SE", ""))
                    emp_name = str(row.get("EMPLYM_STLE_CMMN_MM", ""))
                    job_title = str(row.get("JO_SJ", ""))
                    job_desc = str(row.get("DTY_CN", ""))
                    
                    is_code_pt = emp_code in ("J01103", "J01105")
                    is_text_pt = any(x in emp_name.lower() or x in job_title.lower() or x in job_desc.lower() 
                                     for x in ("시간제", "아르바이트", "알바", "파트타임", "일용직"))
                    
                    if not (is_code_pt or is_text_pt):
                        match = False

                # 5. 청년/주니어 필터링
                if is_youth and match:
                    career_code = str(row.get("CAREER_CND_CMMN_CODE_SE", ""))
                    career_name = str(row.get("CAREER_CND_NM", ""))
                    job_title = str(row.get("JO_SJ", ""))
                    job_desc = str(row.get("DTY_CN", ""))
                    job_code_name = str(row.get("JOBCODE_NM", ""))
                    company_name = str(row.get("CMPNY_NM", ""))
                    
                    # 20대 청년층 아르바이트 및 주니어 구직 성격에 부합하지 않는 시니어 대상 돌봄(요양/간병), 환경 미화(청소), 빌딩 경비/보안, 단순 노무 업종 원천 배제
                    excluded_keywords = (
                        "요양", "요양보호사", "간병", "간병인", "미화", "미화원", "청소", "청소원", "경비", "경비원", 
                        "건물관리", "경비직", "실버케어", "실버", "배출", "시설경비", "단순노무", "주차관리"
                    )
                    
                    if any(x in job_title.lower() or x in job_desc.lower() or x in job_code_name.lower() or x in company_name.lower()
                           for x in excluded_keywords):
                        match = False
                        
                    if match:
                        # J01300 = 경력무관, J01301 = 신입
                        is_entry_or_any = career_code in ("J01300", "J01301") or any(x in career_name for x in ("신입", "무관"))
                        
                        # 3년 이상, 5년 이상 등 고숙련 경력을 노골적으로 요구하는 고연차 채용공고 제외 조건 검출
                        has_heavy_experience = any(x in job_desc.lower() or x in job_title.lower() 
                                                   for x in ("3년 이상", "5년 이상", "7년 이상", "10년 이상"))
                        
                        # 20대 청년층 및 주니어 신입사원이 선호하는 전형적인 아르바이트/정규직 직무 키워드 매칭 분석
                        is_youth_friendly = any(x in job_title.lower() or x in job_desc.lower() or x in job_code_name.lower()
                                                for x in ("청년", "대학생", "초보", "신입", "주니어", "인턴", "학생", "20대", 
                                                          "서빙", "카페", "바리스타", "편의점", "사무", "사무보조", "과외", "학원", 
                                                          "마트", "물류", "패스트푸드", "매장관리", "안내", "조리", "조리사", "복지사", 
                                                          "엔지니어", "개발자", "디자이너", "마케터", "강사", "교사", "어시스턴트", "스태프", "크루"))
                        
                        # [일반 주니어/신입 추가 요청 사항]: 신입 혹은 경력무관이면서 고숙련 경력을 요구하지 않는 일반적인 공고도 포함시킵니다.
                        if not ((is_entry_or_any and not has_heavy_experience) or is_youth_friendly):
                            match = False
                
                if match:
                    logger.info(f"MATCHED JOB - Title: {row.get('JO_SJ')} - Company: {row.get('CMPNY_NM')} - Address: {row.get('WORK_PARAR_BASS_ADRES_CN')}")
                    filtered_rows.append(row)
            
            # 필터링이 완료된 최종 목록을 입력받은 페이지 크기 단위로 후속 분할(슬라이싱)
            total_count = len(filtered_rows)
            slice_start = (start_page - 1) * display
            slice_end = start_page * display
            rows = filtered_rows[slice_start:slice_end]

        # 프론트엔드가 즉시 파싱하기에 최적화된 형태로 데이터 래핑 및 전송
        return {
            "total": total_count,
            "page": start_page,
            "display": len(rows),
            "jobs": rows
        }

    @staticmethod
    async def get_job_detail(wanted_auth_no: str) -> Dict[str, Any]:
        """
        특정 구인 공고의 구인신청번호(JO_REQST_NO)를 대조하여 세부 채용 상세 정보를 반환합니다.
        """
        # 유효한 상세 데이터 포인트를 확보하기 위해 최근 1000개의 활성 채용 목록 풀을 쿼리
        url = f"{settings.seoul_open_data_base_url}/{settings.seoul_open_data_api_key}/json/GetJobInfo/1/1000/"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if "GetJobInfo" in data and "row" in data["GetJobInfo"]:
                    rows = data["GetJobInfo"]["row"]
                    for row in rows:
                        if str(row.get("JO_REQST_NO")) == wanted_auth_no:
                            return row
                
                # 활성 데이터 풀에서 구인 번호를 찾을 수 없는 경우, 연동이 끊어지지 않도록 모의 응답 규격(Fallback Stub)을 자동 조립하여 리턴
                logger.warning(f"Job request number {wanted_auth_no} not found in active batch. Returning stub data.")
                return {
                    "JO_REQST_NO": wanted_auth_no,
                    "CMPNY_NM": "서울 일자리 매칭 기업",
                    "JOBCODE_NM": "채용 정보",
                    "WORK_PARAR_BASS_ADRES_CN": "서울특별시",
                    "DTY_CN": "해당 채용공고는 활성 채용 목록 기간이 만료되었거나 상세 페이지 조회를 지원하지 않는 번호입니다.",
                    "EMPLYM_STLE_CMMN_MM": "상용직",
                    "ACDMCR_NM": "학력무관"
                }
            except Exception as e:
                logger.error(f"Error fetching job details: {e}")
                raise RuntimeError(f"Failed to fetch job detail details: {str(e)}")
