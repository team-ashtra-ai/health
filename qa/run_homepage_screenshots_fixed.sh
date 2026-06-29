#!/usr/bin/env bash
set -u

ROOT="/run/media/code/Storage/GitHub/ashtra/health"
cd "$ROOT" || exit 1

mkdir -p docs/script-runs

REPORT="docs/script-runs/homepage-screenshot-capture-fixed-run.txt"
: > "$REPORT"

log() {
  echo -e "\n========== $1 ==========" | tee -a "$REPORT"
}

run_cmd() {
  echo -e "\n$ $*" | tee -a "$REPORT"
  "$@" 2>&1 | tee -a "$REPORT"
}

is_port_open() {
  python3 - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
s.settimeout(0.35)
try:
    s.connect(("127.0.0.1", port))
    print("open")
except OSError:
    print("closed")
finally:
    s.close()
PY
}

start_server() {
  local port="$1"
  nohup python3 -m http.server "$port" > "docs/script-runs/http-server-${port}.log" 2>&1 &
  echo $! > "docs/script-runs/http-server-${port}.pid"
  sleep 1
}

check_page() {
  python3 - "$1" <<'PY'
import sys, urllib.request
port = int(sys.argv[1])
url = f"http://localhost:{port}/concepts/01-inspire/index.html"
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        text = r.read(800).decode("utf-8", errors="ignore")
    if "Franciele" in text or "<!doctype html>" in text.lower():
        print("ok")
    else:
        print("bad")
except Exception as e:
    print(f"bad: {e}")
PY
}

log "START"
date | tee -a "$REPORT"

log "CURRENT GIT STATE"
run_cmd git branch --show-current
run_cmd git status --short

PORT="8000"

if [ "$(is_port_open 8000)" = "open" ]; then
  echo "Port 8000 is already open." | tee -a "$REPORT"
else
  echo "Starting local server on port 8000..." | tee -a "$REPORT"
  start_server 8000
fi

STATUS="$(check_page 8000)"
echo "Port 8000 page check: $STATUS" | tee -a "$REPORT"

if [ "$STATUS" != "ok" ]; then
  echo "Port 8000 is not serving the repo correctly. Trying 8080..." | tee -a "$REPORT"
  PORT="8080"

  if [ "$(is_port_open 8080)" = "open" ]; then
    echo "Port 8080 is already open." | tee -a "$REPORT"
  else
    echo "Starting local server on port 8080..." | tee -a "$REPORT"
    start_server 8080
  fi

  STATUS="$(check_page 8080)"
  echo "Port 8080 page check: $STATUS" | tee -a "$REPORT"

  if [ "$STATUS" != "ok" ]; then
    echo "ERROR: Could not serve /concepts/01-inspire/index.html on port 8000 or 8080." | tee -a "$REPORT"
    echo "Check docs/script-runs/http-server-8000.log and docs/script-runs/http-server-8080.log" | tee -a "$REPORT"
    exit 1
  fi
fi

log "RUN HOMEPAGE SCREENSHOT CAPTURE"
echo "Using port: $PORT" | tee -a "$REPORT"

run_cmd python3 scripts/capture_homepage_full_screenshots.py --port "$PORT"

log "SCREENSHOT OUTPUT FOLDERS"
find final/homepage-screenshots -maxdepth 2 -type d | sort | tail -20 | tee -a "$REPORT"

log "LATEST SCREENSHOTS"
find final/homepage-screenshots -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.webp" \) | sort | tail -60 | tee -a "$REPORT"

log "DONE"
echo "Report saved to: $REPORT" | tee -a "$REPORT"
echo "Preview URL: http://localhost:${PORT}/select.html" | tee -a "$REPORT"
