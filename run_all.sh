#!/bin/bash
# =====================================================
# 🚀 ESP32 Blackbox All-in-One Startup Script
# =====================================================
# Author: 영민
# Description:
#   재부팅 이후 모든 서비스(Minikube, Mount, Argo, FastAPI, Watch Trigger)를
#   자동으로 복구 및 실행하는 통합 스크립트.
# =====================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🧩 ESP32 Blackbox 통합 실행 스크립트 시작...${NC}"
cd ~/esp32-blackbox || exit 1

# -----------------------------------------------------
echo -e "${GREEN}[1/6] 🔧 Minikube 상태 확인 중...${NC}"
if ! minikube status | grep -q "host: Running"; then
  echo -e "${YELLOW}➡ Minikube가 꺼져 있습니다. 시작합니다...${NC}"
  minikube start --driver=docker
else
  echo "✅ Minikube 이미 실행 중"
fi

# -----------------------------------------------------
echo -e "${GREEN}[2/6] 📂 watch_folder 마운트 확인 및 실행 중...${NC}"
# mount 프로세스 확인
if pgrep -f "minikube mount ~/esp32-blackbox/watch_folder" > /dev/null; then
  echo "✅ mount 이미 실행 중"
else
  echo "➡ mount 실행 중..."
  nohup bash -c "minikube mount ~/esp32-blackbox/watch_folder:/data/watch_folder" \
    > ~/esp32-blackbox/logs/mount.log 2>&1 &
  echo "✅ mount 백그라운드 실행됨"
fi

# -----------------------------------------------------
echo -e "${GREEN}[3/6] 🧠 Argo 서버 상태 확인 중...${NC}"
ARGO_NS="argo"
if ! kubectl get pods -n $ARGO_NS | grep -q "argo-server"; then
  echo -e "${YELLOW}➡ Argo 서버가 감지되지 않음. 다시 적용합니다...${NC}"
  kubectl apply -n $ARGO_NS -f ~/esp32-blackbox/argo/workflows/image-process-auto.yaml
else
  echo "✅ Argo Workflows 정상 실행 중"
fi

# -----------------------------------------------------
echo -e "${GREEN}[4/6] 🐍 FastAPI 서버 실행 중...${NC}"
cd ~/esp32-blackbox/app
if ! pgrep -f "fastapi_server.py" > /dev/null; then
  echo "➡ FastAPI 실행 중..."
  nohup python3 fastapi_server.py > ~/esp32-blackbox/logs/fastapi.log 2>&1 &
  echo "✅ FastAPI 백그라운드 실행됨"
else
  echo "✅ FastAPI 이미 실행 중"
fi

# ==========================================================
echo -e "${GREEN}[5/6] 👀 Watch Trigger 감시 프로세스 실행 중...${NC}"

LOG_DIR="/home/dalls/esp32-blackbox/logs"
WATCH_SCRIPT="/home/dalls/esp32-blackbox/app/watch_trigger.py"

# 로그 디렉터리 없으면 생성
mkdir -p "$LOG_DIR"

# 프로세스 중복 방지 + 백그라운드 실행
if ! pgrep -f "watch_trigger.py" > /dev/null; then
  echo "➡ Watch Trigger 실행 중..."
  nohup python3 "$WATCH_SCRIPT" > "$LOG_DIR/watch_trigger.log" 2>&1 &
  sleep 2
  if pgrep -f "watch_trigger.py" > /dev/null; then
    echo "✅ Watch Trigger 백그라운드 실행됨"
  else
    echo "❌ Watch Trigger 실행 실패 (경로 또는 파이썬 환경 확인 필요)"
  fi
else
  echo "✅ Watch Trigger 이미 실행 중"
fi
# -----------------------------------------------------
echo -e "${GREEN}[6/6] 🌐 Argo Server 포트 포워딩 설정 중...${NC}"
if ! pgrep -f "kubectl port-forward svc/argo-server -n argo" > /dev/null; then
  echo "➡ Port Forward 실행 (localhost:2746)"
  nohup kubectl port-forward svc/argo-server -n argo 2746:2746 \
    > ~/esp32-blackbox/logs/argo_port.log 2>&1 &
  echo "✅ Port Forward 백그라운드 실행됨"
else
  echo "✅ Port Forward 이미 활성화됨"
fi

# -----------------------------------------------------
echo -e "${GREEN}🎉 모든 서비스가 정상적으로 실행되었습니다.${NC}"
echo ""
echo "📍 FastAPI:      http://127.0.0.1:8000"
echo "📍 Argo Server:  http://127.0.0.1:2746"
echo "📍 Watch Folder: ~/esp32-blackbox/watch_folder"
echo ""
echo -e "${YELLOW}⚠️ 주의: mount 프로세스는 백그라운드로 유지됩니다.${NC}"
echo "   (중단하려면:  pkill -f 'minikube mount ~/esp32-blackbox/watch_folder')"
