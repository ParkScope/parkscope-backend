#!/bin/bash
set -e
# Put a sample image under test_images/sample.jpg before running
if [ ! -f test_images/sample.jpg ]; then
  echo "Put a test image at test_images/sample.jpg and re-run"
  exit 1
fi
# ✅ FIX: build from project root, not from docker/
docker build -t esp32-ocr:latest -f docker/Dockerfile .

# Run container mounting test_images
docker run --rm -v $(pwd)/test_images:/data esp32-ocr:latest \
  --input /data/sample.jpg --output /data/sample_out.json

echo "Output written to test_images/sample_out.json"
