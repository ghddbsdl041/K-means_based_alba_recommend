#!/bin/bash

# 에러가 발생하면 스크립트 실행을 즉시 중단합니다.
set -e

echo "=========================================================="
echo " GCP Cloud Run 배포 파이프라인 가동: alba-backend"
echo "=========================================================="

# 활성화된 GCP 계정과 프로젝트 설정 표시
echo "[INFO] 현재 활성화된 GCP 설정 및 프로젝트 정보:"
gcloud config list

# 1. Google Cloud Run 컨테이너 배포 실행
# --source .: 로컬 디렉토리의 Dockerfile을 기반으로 GCP 빌드 가동
# --region us-central1: 설정된 리전
# --project ounse-booth-2026: 사용자의 활성 프로젝트 지정
# --allow-unauthenticated: 외부 프론트엔드 연동을 위한 익명 접근 허용
# --min-instances=1: 콜드 스타트 지연 방지를 위한 상시 기동 인스턴스 1개 구성
# --set-env-vars: 운영 환경용 OpenAPI 키 주입 및 디버그 모드 비활성화
gcloud run deploy alba-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances=1 \
  --set-env-vars="SEOUL_OPEN_DATA_API_KEY=724b6d48746b646837324259507a7a,DEBUG=False"

echo "[SUCCESS] GCP Cloud Run 컨테이너 배포 프로세스가 완료되었습니다!"
echo "=========================================================="
