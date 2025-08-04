# 🅿️ ParkScope Backend

ESP32-CAM 기반 주차 위치 인식 시스템의 백엔드입니다.  
Flask 서버를 통해 이미지를 수신하고, AWS S3에 업로드하며, 이후 Argo Workflow를 통해 후처리 파이프라인을 자동 실행합니다.

---

## ✅ 프로젝트 구조

### 📷 ESP32-CAM → Flask 서버 → S3

1. ESP32-CAM이 주기적으로 사진을 촬영
2. Flask 서버(`/upload`)로 이미지를 POST 전송
3. Flask는 이미지를 로컬에 저장 후, S3 버킷(`esp32cam-project-2025`)의 `uploads/` 폴더로 업로드
4. (다음 단계) S3에 업로드가 완료되면 Argo Workflow가 자동 트리거됨

---

## 📂 디렉토리 설명
```
| 디렉토리 | 설명 |
|----------|------|
| `/uploads` | ESP32-CAM이 전송한 이미지 임시 저장 위치 (서버 로컬) |
| `upload_server.py` | Flask 서버 (이미지 수신 및 업로드 처리) |
| `.env` | AWS 키 등 환경변수 분리 파일 |
| `argo/` | Argo Workflow 정의 및 트리거 코드 (예정) |
| `README.md` | 프로젝트 소개 문서 |
```
---

## ⚙️ 환경 변수 (.env)

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
BUCKET_NAME=esp32cam-project-2025
