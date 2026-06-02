import logging
from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional, Dict, Any
from app.services.recruitment import RecruitmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recruitment", tags=["Recruitment"])

@router.get("/jobs", summary="Search and list job openings")
async def get_jobs(
    keyword: Optional[str] = Query(None, description="검색 키워드 (예: '개발자', '쿠팡')"),
    region: Optional[str] = Query(None, description="지역/자치구 이름 또는 고용24 지역 코드 (예: '강남구', '11000')"),
    occupation: Optional[str] = Query(None, description="모집 직종 코드 또는 직무명"),
    is_part_time: Optional[bool] = Query(None, description="알바/시간제 채용 공고만 필터링 여부"),
    is_youth: Optional[bool] = Query(None, description="20대 청년층 타겟 채용 공고만 필터링 여부 (신입, 경력무관, 청년우대)"),
    start_page: int = Query(1, ge=1, description="조회할 페이지 번호"),
    display: int = Query(10, ge=1, le=500, description="페이지당 출력할 공고 개수"),
    request: Request = None
):
    """
    서울 열린데이터 광장(GetJobInfo)의 실시간 채용 정보 목록을 조회합니다.
    다양한 필터 파라미터 및 페이징 규격을 지원하며, 모든 검색 제어는 백엔드 프록시 단에서 처리됩니다.
    """
    extra_params = {}
    if request:
        exclude_keys = {"keyword", "region", "occupation", "is_part_time", "is_youth", "start_page", "display"}
        for k, v in request.query_params.items():
            if k not in exclude_keys:
                extra_params[k] = v

    try:
        data = await RecruitmentService.get_job_openings(
            keyword=keyword,
            region=region,
            occupation=occupation,
            is_part_time=is_part_time,
            is_youth=is_youth,
            start_page=start_page,
            display=display,
            extra_params=extra_params
        )
        return data
    except Exception as e:
        logger.error(f"get_jobs 엔드포인트 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{wanted_auth_no}", summary="Get job opening details")
async def get_job_detail(wanted_auth_no: str):
    """
    구인신청번호(JO_REQST_NO)를 기준으로 특정 구인 공고의 상세 요강 정보를 조회합니다.
    """
    try:
        data = await RecruitmentService.get_job_detail(wanted_auth_no=wanted_auth_no)
        return data
    except Exception as e:
        logger.error(f"get_job_detail 엔드포인트 호출 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
