#!/usr/bin/env python3
import os
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ======================
# 환경 설정
# ======================
WATCH_DIR = "/home/dalls/esp32-blackbox/watch_folder"
WORKFLOW_FILE = "/home/dalls/esp32-blackbox/argo/workflows/image-process-auto.yaml"
LOG_FILE = "/home/dalls/esp32-blackbox/logs/watch_trigger.log"

# ======================
# 로깅 설정
# ======================
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)

# ======================
# 감시 핸들러 정의
# ======================
class WatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if filename.lower().endswith(".jpg"):
            logging.info(f"📸 Detected new image: {filename}")

            # Argo 워크플로우 트리거
            try:
                cmd = [
                    "argo", "submit", "-n", "argo",
                    WORKFLOW_FILE,
                    "--parameter", f"input={filename}",
                    "--watch"
                ]
                logging.info(f"🚀 Running Argo command: {' '.join(cmd)}")

                subprocess.run(cmd, check=True)
                logging.info(f"✅ Workflow triggered for {filename}")

                # 처리 후 원본 파일 삭제
                os.remove(filepath)
                logging.info(f"🗑️ Deleted source image: {filename}")

            except subprocess.CalledProcessError as e:
                logging.error(f"❌ Argo workflow failed: {e}")
            except Exception as e:
                logging.error(f"⚠️ Unexpected error: {e}")

# ======================
# 감시 루프 시작
# ======================
if __name__ == "__main__":
    logging.info("👀 Starting Watch Trigger Service...")
    if not os.path.exists(WATCH_DIR):
        os.makedirs(WATCH_DIR)

    event_handler = WatchHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    logging.info(f"📂 Watching folder: {WATCH_DIR}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("🛑 Watch Trigger stopped manually.")
    observer.join()
