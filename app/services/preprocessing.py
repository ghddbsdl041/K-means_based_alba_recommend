import re
from typing import List, Dict, Any

class PreprocessingService:
    @staticmethod
    def preprocess_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_data = []
        for job in jobs:
            # 텍스트 검색을 위해 모든 관련 문자열 필드를 하나로 합침
            full_text = f"{job.get('title', '')} {job.get('company_name', '')} {job.get('work_time', '')} {job.get('pay_info', '')} {job.get('conditions', '')} {job.get('work_days', '')} {job.get('work_period', '')} {job.get('category', '')}"
            
            # 1. pay_amount (시급, 급여협의 예외 처리 및 단위 통일)
            pay_type = job.get("pay_type", "시급")
            pay_info = job.get("pay_info", "")
            pay_numbers = re.sub(r'[^0-9]', '', pay_info)
            pay_amount = int(pay_numbers) if pay_numbers else 0
            
            # (추가 피처 생성용 임시 변수, 실제 시간 파싱은 뒤에서 이뤄지므로 기본값 8시간 가정)
            temp_duration = 8 
            
            # 급여 단위를 '시급'으로 통일 (월급, 일급, 주급 변환)
            if pay_type == "월급" or "월급" in pay_info:
                pay_amount = pay_amount // 209 # 주휴수당 포함 월 기본 근로시간
            elif pay_type == "일급" or "일급" in pay_info:
                pay_amount = pay_amount // temp_duration
            elif pay_type == "주급" or "주급" in pay_info:
                pay_amount = pay_amount // (temp_duration * 5)
            elif pay_type == "연봉" or "연봉" in pay_info:
                pay_amount = pay_amount // (209 * 12)
                
            # 이상치(Outlier) 처리 (Clipping/Winsorization)
            # K-Means 계산 시 왜곡을 막기 위해 시급 하한선(최저시급)과 상한선 설정
            if pay_amount < 10320:
                pay_amount = 10320
            if pay_amount > 50000:
                pay_amount = 50000 # 지나치게 높은 시급(의도적 어그로, 오류)은 5만원으로 상한선 고정
            
            # 2. work_time (시간협의 예외 처리 및 근무 시간(duration) 계산 추가)
            work_time_str = job.get("work_time", "")
            time_match = re.search(r'(\d{1,2}):\d{2}\s*~\s*(\d{1,2}):\d{2}', work_time_str)
            is_negotiable_time = 0
            if time_match:
                start_time = int(time_match.group(1))
                end_time = int(time_match.group(2))
                if end_time < start_time:
                    end_time += 24 # 야간/새벽을 넘기는 경우
                work_duration = end_time - start_time
            else:
                # 시작 시간만 있거나 협의인 경우 (기본값 세팅)
                single_match = re.search(r'(\d{1,2}):\d{2}', work_time_str)
                if single_match:
                    start_time = int(single_match.group(1))
                    work_duration = 6 # 알 수 없는 경우 평균 근로시간 6시간으로 대체
                else:
                    start_time = 12 # 시간협의 등 매칭 안될 시 중앙값 12시로 대체
                    work_duration = 6
                    is_negotiable_time = 1 if "협의" in work_time_str else 0
                
            # 3. 제안된 세분화 이진 피처 (조건 파싱)
            
            # (1) 4대보험 (안정성)
            is_insured = 1 if any(kw in full_text for kw in ["고용보험", "산재보험", "국민연금", "건강보험", "4대보험"]) else 0
            
            # (2) 수당 및 보상 (추가 수입 / 성과 보상)
            is_incentive_bonus = 1 if any(kw in full_text for kw in ["인센티브제", "정기보너스", "우수사원", "장기근속수당"]) else 0
            is_overtime_pay = 1 if any(kw in full_text for kw in ["연장근로수당", "휴일근로수당", "야간근로수당"]) else 0
            is_severance_pay = 1 if any(kw in full_text for kw in ["퇴직금", "퇴직연금"]) else 0
            is_same_day_pay = 1 if any(kw in full_text for kw in ["당일지급", "일급", "주급"]) else 0 # 당일/단기 현금지급성 알바 피처 추가
            
            # (3) 휴가 및 휴식 (워라밸)
            is_leave = 1 if any(kw in full_text for kw in ["연차", "월차", "정기휴가", "연월차수당", "휴게시간"]) else 0
            is_condolence = 1 if any(kw in full_text for kw in ["경조휴가제", "각종 경조금", "경조금"]) else 0
            
            # (4) 복리후생 및 편의 (근무 환경)
            is_meal_provided = 1 if any(kw in full_text for kw in ["점심제공", "석식제공", "조식제공", "식비(식사) 지원"]) else 0
            is_uniform_provided = 1 if "근무복 지급" in full_text else 0
            is_parking_available = 1 if any(kw in full_text for kw in ["주차가능", "주차비지원"]) else 0
            
            # (5) 지원자 우대 조건 (진입 장벽)
            is_beginner_friendly = 1 if any(kw in full_text for kw in ["초보 가능", "초보가능"]) else 0
            is_experienced_preferred = 1 if any(kw in full_text for kw in ["동종업종경력", "동종업계 경력자"]) else 0
            is_student_preferred = 1 if any(kw in full_text for kw in ["대학생우대", "대학휴학생우대", "대학재학생 가능", "대학휴학생 가능"]) else 0
            is_nearby_preferred = 1 if any(kw in full_text for kw in ["인근지역우대", "인근거주자"]) else 0
            is_friends_ok = 1 if any(kw in full_text for kw in ["친구와함께가능", "친구와함께"]) else 0
            is_long_term_ok = 1 if any(kw in full_text for kw in ["장기근무", "장기근속"]) else 0
            
            # (6) 근무 일정 및 요일 예외 처리 (주 5일, 주 6일, 월~토, 협의 등)
            # 월~토, 주 6일은 평일과 주말 속성을 동시에 가지도록 처리합니다.
            is_weekend = 1 if any(kw in full_text for kw in ["주말", "토,일", "토~일", "월~토", "월~일", "주 6일", "주6일", "주 7일"]) else 0
            is_weekday = 1 if any(kw in full_text for kw in ["월~금", "평일", "주 5일", "주5일", "월~토", "월~일", "주 6일", "주6일", "주 7일"]) else 0
            # 주 2~4일, 요일협의 등은 유동적 스케줄로 분류합니다.
            is_negotiable_days = 1 if any(kw in full_text for kw in ["요일협의", "주 1일", "주1일", "주 2일", "주2일", "주 3일", "주3일", "주 4일", "주4일"]) else 0
            
            is_short = 1 if "1주일" in full_text or "1개월" in full_text or "하루" in full_text else 0
            
            # (7) 직종 대분류 원-핫 인코딩 (category)
            cat_str = job.get("category", "")
            is_admin = 1 if any(kw in cat_str for kw in ["사무보조", "데이터입력"]) else 0
            is_cs = 1 if any(kw in cat_str for kw in ["고객상담", "인바운드", "텔레마케팅", "아웃바운드"]) else 0
            is_food = 1 if any(kw in cat_str for kw in ["바리스타", "카페", "커피전문점", "음식점", "주방", "서빙"]) else 0
            is_retail = 1 if any(kw in cat_str for kw in ["판매", "매장관리", "편의점", "쇼핑몰"]) else 0
            is_physical = 1 if any(kw in cat_str for kw in ["배달", "물류", "청소", "경비", "노무", "택배"]) else 0
            # 위 5개 어디에도 속하지 않으면 etc
            is_etc = 1 if not any([is_admin, is_cs, is_food, is_retail, is_physical]) else 0
            
            # (8) 근무 시간대 파생 피처 (start_time 기준)
            # is_morning_shift: 06:00 ~ 11:59 시작
            # is_afternoon_shift: 12:00 ~ 17:59 시작
            # (8) 근무 시간대 (Shift) 이진 분류
            is_morning_shift = 1 if 6 <= start_time < 12 else 0
            is_afternoon_shift = 1 if 12 <= start_time < 18 else 0
            is_night_shift = 1 if start_time >= 18 or start_time < 6 else 0
            
            # (9) 지역(Region) 파싱 (K-Means 학습용이 아닌, 사후 분석 및 필터링용 메타데이터)
            # 예: "서울 강남구 역삼동" -> city: "서울", district: "강남구"
            region_str = job.get("region", "")
            region_parts = region_str.split(" ")
            city = region_parts[0] if len(region_parts) > 0 and region_parts[0] else "알수없음"
            district = region_parts[1] if len(region_parts) > 1 else "알수없음"
            
            processed_data.append({
                "original_job": job,
                "location": {
                    "city": city,
                    "district": district
                },
                "features": {
                    "pay_amount": pay_amount,
                    "work_time": start_time,
                    "work_duration": work_duration,
                    "is_negotiable_time": is_negotiable_time,
                    "is_negotiable_days": is_negotiable_days,
                    "is_insured": is_insured,
                    "is_incentive_bonus": is_incentive_bonus,
                    "is_overtime_pay": is_overtime_pay,
                    "is_severance_pay": is_severance_pay,
                    "is_same_day_pay": is_same_day_pay,
                    "is_leave": is_leave,
                    "is_condolence": is_condolence,
                    "is_meal_provided": is_meal_provided,
                    "is_uniform_provided": is_uniform_provided,
                    "is_parking_available": is_parking_available,
                    "is_beginner_friendly": is_beginner_friendly,
                    "is_experienced_preferred": is_experienced_preferred,
                    "is_student_preferred": is_student_preferred,
                    "is_nearby_preferred": is_nearby_preferred,
                    "is_friends_ok": is_friends_ok,
                    "is_long_term_ok": is_long_term_ok,
                    "is_weekend": is_weekend,
                    "is_weekday": is_weekday,
                    "is_short": is_short,
                    "is_admin": is_admin,
                    "is_cs": is_cs,
                    "is_food": is_food,
                    "is_retail": is_retail,
                    "is_physical": is_physical,
                    "is_etc": is_etc,
                    "is_morning_shift": is_morning_shift,
                    "is_afternoon_shift": is_afternoon_shift,
                    "is_night_shift": is_night_shift
                }
            })
            
        return processed_data
