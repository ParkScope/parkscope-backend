from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# ==============================
# 기본 환경 설정
# ==============================
WATCH_DIR = os.path.expanduser("~/esp32-blackbox/watch_folder")
os.makedirs(WATCH_DIR, exist_ok=True)

app = FastAPI(
    title="ESP32-CAM Parking OCR API",
    description="FastAPI backend for vehicle parking location recognition system.",
    version="2.0.0"
)


# =========================================================
# [1] 기본 상태 확인
# =========================================================
@app.get("/")
async def root():
    """서버 상태 확인용"""
    return JSONResponse({"message": "ESP32-CAM OCR API is running."})


# =========================================================
# [2] 이미지 업로드 (ESP32-CAM)
# =========================================================
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    ESP32-CAM에서 전송된 이미지를 저장.
    Argo Workflow가 감시할 watch_folder에 저장함.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp32_{timestamp}.jpg"
        save_path = os.path.join(WATCH_DIR, filename)

        # TODO: 실제 저장
        # contents = await file.read()
        # with open(save_path, "wb") as f:
        #     f.write(contents)

        print(f"[UPLOAD] Received and saved: {filename}")
        return JSONResponse({"status": "ok", "filename": filename})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


# =========================================================
# [3] 최신 OCR 결과 조회
# =========================================================
@app.get("/result/latest")
async def get_latest_result():
    """
    최근 분석된 OCR 결과 반환
    TODO: 분석 완료된 JSON 결과 파일 불러오기
    """
    dummy_result = {
        "status": "done",
        "text": "A12",
        "confidence": 0.94,
        "timestamp": "2025-10-17T13:12:00"
    }
    return JSONResponse(dummy_result)


# =========================================================
# [4] 차량 번호 업로드 (보류)
# =========================================================
@app.post("/vehicle/plate")
async def upload_plate():
    """
    차량번호 정보 업로드 (ESP32가 OCR 결과로 전송 예정)
    TODO: 번호판 인식 결과 수신 처리
    """
    return JSONResponse({
        "status": "pending",
        "detail": "vehicle plate upload endpoint - not implemented yet"
    })


# =========================================================
# [5] 자동차 위치 인식 결과 조회
# =========================================================
@app.get("/vehicle/location")
async def get_vehicle_location():
    """
    OCR 분석 결과 기반 주차 위치 정보 반환
    TODO: 실제 결과 파일 or DB 기반으로 위치 계산
    """
    result = {
        "status": "done",
        "location": "B2-A12",
        "timestamp": "2025-10-17T13:15:00"
    }
    return JSONResponse(result)


# =========================================================
# [6] 기둥 사진 업로드 (ESP32 → 서버)
# =========================================================
@app.post("/vehicle/pillar/photo")
async def upload_pillar_photo(file: UploadFile = File(...)):
    """
    ESP32에서 전송한 기둥 이미지 저장
    TODO: watch_folder/pillar_*.jpg 형태로 저장 후 OCR 트리거
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pillar_{timestamp}.jpg"
        save_path = os.path.join(WATCH_DIR, filename)

        # TODO: 실제 저장
        # contents = await file.read()
        # with open(save_path, "wb") as f:
        #     f.write(contents)

        print(f"[UPLOAD] Pillar photo received: {filename}")
        return JSONResponse({"status": "ok", "filename": filename})
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


# =========================================================
# [7] 기둥 사진 조회 (최근 파일 or 분석 결과)
# =========================================================
@app.get("/vehicle/pillar/photo")
async def get_pillar_photo():
    """
    최근 기둥 이미지 조회
    TODO: watch_folder 내 최신 이미지 파일을 찾아서 반환
    """
    # 더미 데이터
    return JSONResponse({
        "status": "ok",
        "photo_url": "http://localhost:8000/static/images/pillar_latest.jpg"
    })


# =========================================================
# [8] 층별 차량 대수 통계
# =========================================================
@app.get("/vehicle/statistics")
async def get_parking_statistics():
    """
    층별 주차 차량 수 통계 반환
    TODO: DB 또는 로컬 JSON 기반으로 실제 값 계산
    """
    stats = [
        {"floor": "B1", "count": 37},
        {"floor": "B2", "count": 42},
        {"floor": "B3", "count": 29}
    ]
    return JSONResponse({"status": "ok", "data": stats})


# =========================================================
# [실행부]
# =========================================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server at http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
