import easyocr
import json
import time
import sys
import os
from PIL import Image

def main():
    start = time.time()

    # 입력 이미지 경로
    input_path = "/data/sample.jpg"
    output_path = "/data/sample_out.json"

    if not os.path.exists(input_path):
        print(f"[ERROR] Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # EasyOCR Reader 초기화
    reader = easyocr.Reader(['en'], gpu=False)

    # OCR 수행
    results = reader.readtext(input_path)

    # 결과 구성
    recognized = []
    for (bbox, text, conf) in results:
        recognized.append({
            "text": text,
            "conf": float(conf),
            "bbox": [int(p[0]) for p in bbox]
        })

    output = {
        "file": os.path.basename(input_path),
        "recognized": recognized,
        "processing_ms": int((time.time() - start) * 1000)
    }

    # 결과 저장
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[DONE] OCR completed → {output_path}")

if __name__ == "__main__":
    main()

