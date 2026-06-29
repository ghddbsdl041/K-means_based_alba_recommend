from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import sqlite3
import pandas as pd
import joblib
import random
from typing import List, Optional

from app.services.preprocessing import PreprocessingService
from app.config import settings

router = APIRouter(
    prefix="/api/recommend",
    tags=["Recommend"]
)

class SurveyRequest(BaseModel):
    q1_answer: str = Field(..., description="Q1 대답 (A: 급전/단기, B: 꾸준히/안정성)")
    q2_answer: Optional[str] = Field(None, description="Q2 대답 (A: 실내/사무, B: 현장/서비스) - Q1이 B일 때만 필수")
    q3_answer: Optional[str] = Field(None, description="Q3 대답 (A: 가벼운 파트타임, B: 풀타임 정규직급) - Q2가 B일 때만 필수")
    q4_answer: str = Field(..., description="Q4 대답 (A: 주간 선호, B: 야간 선호)")
    q5_answer: str = Field(..., description="Q5 대답 (A: 평일 위주, B: 주말 위주)")
    limit: int = Field(100, description="반환할 추천 알바 개수")

class RecommendedJob(BaseModel):
    cluster_id: int
    cluster_name: str
    company_name: str
    title: str
    pay_info: str
    work_time: str
    region: str
    detail_url: str
    category: str

def get_cluster_id_from_survey(survey: SurveyRequest) -> tuple[int, str]:
    if survey.q1_answer.upper() == 'A':
        return 1, "고수익 단기/노무형"
    elif survey.q1_answer.upper() == 'B':
        if not survey.q2_answer:
            raise HTTPException(status_code=400, detail="Q1이 B인 경우 Q2 응답이 필요합니다.")
        
        if survey.q2_answer.upper() == 'A':
            return 0, "안정적 사무/CS형"
        elif survey.q2_answer.upper() == 'B':
            if not survey.q3_answer:
                raise HTTPException(status_code=400, detail="Q2가 B인 경우 Q3 응답이 필요합니다.")
                
            if survey.q3_answer.upper() == 'A':
                return 2, "일반 파트타임 서비스형"
            elif survey.q3_answer.upper() == 'B':
                return 3, "정규 식음료/매장관리형"
            
    raise HTTPException(status_code=400, detail="잘못된 설문 응답 형식입니다.")

@router.post("", response_model=List[RecommendedJob])
async def recommend_jobs(survey: SurveyRequest):
    """
    사용자의 설문(Q1, Q2, Q3) 결과를 바탕으로 K-Means 군집을 매칭하고 맞춤형 알바를 실시간으로 추천합니다.
    """
    target_cluster_id, cluster_name = get_cluster_id_from_survey(survey)
    
    # 1. DB에서 최신 알바 공고 가져오기
    # 실시간 추천을 위해 매번 최신 데이터를 조회
    import os
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    
    # 프론트엔드에 알바천국 및 알바몬 데이터를 모두 노출하도록 추출 (최신 공고 순정렬)
    query = "SELECT * FROM crawled_jobs WHERE source IN ('AlbaHeaven', 'Albamon') ORDER BY updated_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="추천할 알바 데이터가 없습니다.")

    # 회사명 + 제목 기준으로 중복 제거 (가장 최신 등록된 공고만 유지)
    df = df.drop_duplicates(subset=['company_name', 'title'], keep='first')

    # 2. 전처리 파이프라인 수행
    jobs_dict = df.to_dict('records')
    preprocessed = PreprocessingService.preprocess_jobs(jobs_dict)
    
    features_list = [item["features"] for item in preprocessed]
    features_df = pd.DataFrame(features_list)
    
    # 3. 모델 로드 및 실시간 추론 (Inference)
    try:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scaler_path = os.path.join(app_dir, 'models', 'scaler.pkl')
        kmeans_path = os.path.join(app_dir, 'models', 'kmeans_k4.pkl')
        scaler = joblib.load(scaler_path)
        kmeans = joblib.load(kmeans_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="모델 파일을 찾을 수 없습니다. 학습이 완료되었는지 확인하세요.")
        
    scaled_data = scaler.transform(features_df)
    predictions = kmeans.predict(scaled_data)
    
    # 4. 타겟 군집 필터링 및 결과 생성 (하이브리드 추천)
    matched_jobs = []
    for i, pred_cluster in enumerate(predictions):
        if pred_cluster == target_cluster_id:
            job_info = preprocessed[i]["original_job"]
            features = preprocessed[i]["features"]
            
            # 사용자 설문 의도에 가장 완벽하게 부합하는 공고를 위로 올리기 위한 가중치(Score) 계산
            score = 0
            if target_cluster_id == 0:
                # 사무직/CS: 관련 피처 가중치 부여
                score = features.get("is_admin", 0) * 10 + features.get("is_cs", 0) * 10
            elif target_cluster_id == 1:
                # 단기 고수익: 당일지급 및 시급 가중치
                score = features.get("is_same_day_pay", 0) * 10 + (features.get("pay_amount", 0) / 10000)
            elif target_cluster_id == 2:
                # 파트타임: 근무시간이 짧을수록 가중치
                duration = features.get("work_duration", 8)
                score = (10 - duration) * 2 if duration < 8 else 0
            elif target_cluster_id == 3:
                # 풀타임 정규직: 4대보험 및 식음료 매장 가중치
                score = features.get("is_insured", 0) * 10 + features.get("is_food", 0) * 5
                
            # 4번 질문(시간대)에 따른 가중치
            if survey.q4_answer.upper() == 'A':
                # 주간 선호: 아침/오후 시간대 공고 가중치 부여
                score += features.get("is_morning_shift", 0) * 5 + features.get("is_afternoon_shift", 0) * 5
            elif survey.q4_answer.upper() == 'B':
                # 야간 선호: 저녁/심야 시간대 공고 가중치 부여
                score += features.get("is_night_shift", 0) * 10
                
            # 5번 질문(주말/평일)에 따른 가중치
            if survey.q5_answer.upper() == 'A':
                # 평일 위주: 주말 근무가 아닌(0) 곳 가중치 부여
                if features.get("is_weekend", 0) == 0:
                    score += 5
            elif survey.q5_answer.upper() == 'B':
                # 주말 위주: 주말 근무(1) 가중치 부여
                score += features.get("is_weekend", 0) * 10
                
            matched_jobs.append({
                "score": score,
                "source": job_info.get("source"),
                "job": RecommendedJob(
                    cluster_id=int(pred_cluster),
                    cluster_name=cluster_name,
                    company_name=job_info.get("company_name", "알수없음"),
                    title=job_info.get("title", ""),
                    pay_info=job_info.get("pay_info", ""),
                    work_time=job_info.get("work_time", ""),
                    region=job_info.get("region", ""),
                    detail_url=job_info.get("detail_url", "").replace("/recruitment/", "/jobs/"),
                    category=job_info.get("category", "")
                )
            })
            
    # 알바천국 30% : 알바몬 70% 비율 조정을 위한 분할 및 정렬
    heaven_jobs = [item for item in matched_jobs if item["source"] == "AlbaHeaven"]
    mon_jobs = [item for item in matched_jobs if item["source"] == "Albamon"]
    
    heaven_jobs.sort(key=lambda x: x["score"], reverse=True)
    mon_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # 목표 개수 계산
    target_heaven = int(survey.limit * 0.3)
    target_mon = survey.limit - target_heaven
    
    # 실제 추출 개수 결정 (한쪽에 데이터가 부족할 경우 다른 쪽에서 보충)
    actual_heaven = min(target_heaven, len(heaven_jobs))
    actual_mon = min(target_mon, len(mon_jobs))
    
    if actual_heaven < target_heaven:
        actual_mon = min(survey.limit - actual_heaven, len(mon_jobs))
    elif actual_mon < target_mon:
        actual_heaven = min(survey.limit - actual_mon, len(heaven_jobs))
        
    # 병합 및 최종 스코어 내림차순 정렬
    selected_items = heaven_jobs[:actual_heaven] + mon_jobs[:actual_mon]
    selected_items.sort(key=lambda x: x["score"], reverse=True)
    
    recommended_jobs = [item["job"] for item in selected_items]
    return recommended_jobs
