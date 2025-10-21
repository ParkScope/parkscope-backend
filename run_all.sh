#!/bin/bash
# ============================================
# 🚗 ESP32 Blackbox All-in-One Startup Script
# ============================================
# Author: 영민
# Description:
#   부팅 이후 모든 서비스(Minikube, Mount, Argo, FastAPI, Watch Trigger, Ngrok)
#   를 자동 복구 및 실행하는 통합 스크립트
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 ESP32 Blackbox 통합 실행 스크립트 시작...${NC}"
cd /home/dalls/esp32-blackbox || exit 1

# ============================================
# [1/7] 🧩 Minikube 상태 확인 및 실행
# ============================================
echo -e "${GREEN}[1/7] 🔧 Minikube 상태 확인 중...${NC}"
if ! minikube status | grep -q "host: Running"; then
  echo -e "${YELLOW}⚠️ Minikube가 꺼져 있습니다. 시작합니다...${NC}"
  minikube start --driver=docker
else
  echo -e "✅ Minikube 이미 실행 중"
fi

# ============================================
# [2/7] 📁 watch_folder 마운트 확인 및 실행
# ============================================
echo -e "${GREEN}[2/7] 📁 watch_folder 마운트 확인 중...${NC}"
if pgrep -f "minikube mount /home/dalls/esp32-blackbox/watch_folder" > /dev/null; then
  echo -e "✅ mount 이미 실행 중"
else
  echo -e "🟡 mount 실행 중..."
  nohup bash -c "minikube mount /home/dalls/esp32-blackbox/watch_folder:/data/watch_folder" \
    > /home/dalls/esp32-blackbox/logs/mount.log 2>&1 &
  echo -e "✅ mount 백그라운드 실행됨"
fi

# ============================================
# [3/7] 🧠 Argo Workflows 상태 확인 및 복구
# ============================================
echo -e "${GREEN}[3/7] 🧠 Argo 서버 상태 확인 중...${NC}"
ARGO_NS="argo"
if ! kubectl get pods -n $ARGO_NS | grep -q "argo-server"; then
  echo -e "${YELLOW}⚠️ Argo 서버가 감지되지 않음. 다시 적용합니다...${NC}"
  kubectl apply -n $ARGO_NS -f /home/dalls/esp32-blackbox/argo/workflows/image-process-auto.yaml
else
  echo -e "✅ Argo Workflows 정상 실행 중"
fi

# ============================================
# [4/7] 🧩 FastAPI 서버 실행
# ============================================
echo -e "${GREEN}[4/7] 🧩 FastAPI 서버 실행 중...${NC}"
cd /home/dalls/esp32-blackbox/app
if pgrep -f "fastapi_server.py" > /dev/null; then
  echo -e "✅ FastAPI 이미 실행 중"
else
  echo -e "🟡 FastAPI 실행 중..."
  nohup python3 fastapi_server.py > /home/dalls/esp32-blackbox/logs/fastapi.log 2>&1 &
  echo -e "✅ FastAPI 백그라운드 실행됨"
fi

# ============================================
# [5/7] 👀 Watch Trigger 감시 프로세스 실행
# ============================================
echo -e "${GREEN}[5/7] 👀 Watch Trigger 실행 중...${NC}"
LOG_DIR="/home/dalls/esp32-blackbox/logs"
WATCH_SCRIPT="/home/dalls/esp32-blackbox/app/watch_trigger.py"
mkdir -p "$LOG_DIR"

if pgrep -f "watch_trigger.py" > /dev/null; then
  echo -e "✅ Watch Trigger 이미 실행 중"
else
  echo -e "🟡 Watch Trigger 실행 중..."
  nohup python3 "$WATCH_SCRIPT" > "$LOG_DIR/watch_trigger.log" 2>&1 &
  echo -e "✅ Watch Trigger 백그라운드 실행됨"
fi

# ============================================
# [6/7] 🌐 Argo Server 포트 포워딩 설정
# ============================================
echo -e "${GREEN}[6/7] 🌐 Argo Server 포트 포워딩 설정 중...${NC}"
if pgrep -f "kubectl port-forward svc/argo-server -n argo" > /dev/null; then
  echo -e "✅ Port Forward 이미 활성화됨"
else
  echo -e "🟡 Port Forward 실행 (localhost:2746)"
  nohup kubectl port-forward svc/argo-server -n argo 2746:2746 \
    > /home/dalls/esp32-blackbox/logs/argo_port.log 2>&1 &
  echo -e "✅ Port Forward 백그라운드 실행됨"
fi

# ============================================
# [7/7] 🌎 Ngrok (고정 도메인) 실행
# ============================================
echo -e "${GREEN}[7/7] 🌎 Ngrok 도메인 실행 중...${NC}"
if pgrep -f "ngrok http --url=park-scope.ngrok-free.dev 8000" > /dev/null; then
  echo -e "✅ Ngrok 이미 실행 중"
else
  echo -e "🟡 Ngrok 실행 시작..."
  nohup ngrok http --url=park-scope.ngrok-free.dev 8000 \
    > /home/dalls/esp32-blackbox/logs/ngrok.log 2>&1 &
  echo -e "✅ Ngrok 백그라운드 실행됨 (https://park-scope.ngrok-free.dev)"
fi

# ============================================
# 완료 메시지
# ============================================
echo ""
echo -e "${GREEN}🎉 모든 서비스가 정상적으로 실행되었습니다.${NC}"
echo ""
echo -e "🌐 FastAPI:      http://127.0.0.1:8000"
echo -e "🔗 Ngrok URL:    https://park-scope.ngrok-free.dev"
echo -e "🧠 Argo Server:  http://127.0.0.1:2746"
echo -e "📂 Watch Folder: /home/dalls/esp32-blackbox/watch_folder"
echo ""
echo -e "${YELLOW}⚠️ mount 프로세스는 백그라운드로 유지됩니다.${NC}"
echo -e "(중단하려면: pkill -f 'minikube mount /home/dalls/esp32-blackbox/watch_folder')"
echo ""
