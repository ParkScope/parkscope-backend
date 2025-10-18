from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

# 업로드 저장 경로
WATCH_DIR = os.path.expanduser("~/esp32-blackbox/watch_folder")

app = FastAPI()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 파일명 timestamp로 변경하여 중복 방지
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"esp32_{timestamp}.jpg"
        save_path = os.path.join(WATCH_DIR, filename)

        # 저장
        with open(save_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        print(f"[UPLOAD] Saved new image: {filename}")
        return JSONResponse(content={"status": "ok", "filename": filename})

    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
