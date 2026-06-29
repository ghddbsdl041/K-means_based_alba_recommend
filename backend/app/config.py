import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # 서울 열린데이터 광장 API 인증키
    seoul_open_data_api_key: str = Field(..., validation_alias="SEOUL_OPEN_DATA_API_KEY")

    # 서울 열린데이터 광장 오픈API 기본 연동 엔드포인트 URL
    seoul_open_data_base_url: str = "http://openapi.seoul.go.kr:8088"

    # 알바몬/알바천국 크롤링 타겟 URL 및 User-Agent 설정
    albamon_univ_url: str = "https://www.albamon.com/list/gi/mon_univ.asp"
    albaheaven_univ_url: str = "https://www.alba.co.kr/job/category/MainUniv.asp"
    crawler_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # API 게이트웨이 서버 구동 환경 설정
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    database_url: str = Field("sqlite+aiosqlite:///alba.db", validation_alias="DATABASE_URL")


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# 싱글톤 패턴 기반 전역 설정 객체 생성
settings = Settings()
