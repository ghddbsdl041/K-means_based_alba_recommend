import re
from typing import List, Dict, Any

class PreprocessingService:
    @staticmethod
    def preprocess_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_data = []
        for job in jobs:
            # 텍스트 검색을 위해 모든 문자열 필드를 하나로 합침
            full_text = f"{job.get('title', '')} {job.get('company_name', '')} {job.get('work_time', '')} {job.get('pay_info', '')} {job.get('conditions', '')}"
            
            # 1. pay_amount
            pay_info = job.get("pay_info", "")
            # 숫자만 추출 (예: 시급 10,000 -> 10000)
            pay_numbers = re.sub(r'[^0-9]', '', pay_info)
            pay_amount = int(pay_numbers) if pay_numbers else 0
            
            # 2. work_time
            work_time_str = job.get("work_time", "")
            time_match = re.search(r'(\d{1,2}):\d{2}', work_time_str)
            if time_match:
                start_time = int(time_match.group(1))
            else:
                start_time = 12 # 시간협의 등 매칭 안될 시 중앙값으로 대체
                
            # 3. 이진 피처 (조건 파싱)
            is_meal = 1 if "점심제공" in full_text or "석식제공" in full_text else 0
            is_night = 1 if "야간근로수당" in full_text or "야간교통비" in full_text else 0
            is_beginner = 1 if "초보가능" in full_text else 0
            is_student = 1 if "대학생우대" in full_text or "대학재학생" in full_text else 0
            is_insurance = 1 if "4대보험" in full_text or "국민연금" in full_text else 0
            
            # 4. work_days
            is_weekend = 1 if "주말" in full_text or "토,일" in full_text else 0
            is_weekday = 1 if "월~금" in full_text else 0
            
            # 5. work_period
            is_short = 1 if "1주일" in full_text or "1개월" in full_text or "하루" in full_text else 0
            
            processed_data.append({
                "original_job": job,
                "features": {
                    "pay_amount": pay_amount,
                    "work_time": start_time,
                    "is_meal": is_meal,
                    "is_night": is_night,
                    "is_beginner": is_beginner,
                    "is_student": is_student,
                    "is_insurance": is_insurance,
                    "is_weekend": is_weekend,
                    "is_weekday": is_weekday,
                    "is_short": is_short
                }
            })
            
        return processed_data
