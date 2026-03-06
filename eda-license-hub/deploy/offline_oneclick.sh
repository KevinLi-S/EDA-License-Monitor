#!/usr/bin/env bash
set -euo pipefail

# Auto-detect app dir (parent of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_DIR=${LOG_DIR:-/var/log/license-portal}
LICENSE_DIR=${LICENSE_DIR:-/eda/env/license}
RUNTIME_DIR="$APP_DIR/runtime/miniconda"

cd "$APP_DIR"

echo "========================================"
echo "Deploy EDA License Hub (offline)"
echo "========================================"
echo "APP_DIR=$APP_DIR"
echo "LOG_DIR=$LOG_DIR"
echo "LICENSE_DIR=$LICENSE_DIR"
echo ""

[[ -f runtime/Miniconda3-Linux-x86_64.sh ]] || { echo "Missing runtime/Miniconda3-Linux-x86_64.sh"; exit 1; }
[[ -d backend/offline/wheels-linux ]] || { echo "Missing backend/offline/wheels-linux"; exit 1; }
[[ -d frontend/dist ]] || { echo "Missing frontend/dist"; exit 1; }

echo "[1/7] Install embedded Python runtime"
bash runtime/Miniconda3-Linux-x86_64.sh -b -p "$RUNTIME_DIR"
export PATH="$RUNTIME_DIR/bin:$PATH"

echo "[2/7] Create backend venv"
python -m venv backend/.venv
source backend/.venv/bin/activate

PYVER=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Embedded Python version: $PYVER"
if [[ "$PYVER" != "3.8" ]]; then
  echo "ERROR: expected embedded Python 3.8, got $PYVER"
  exit 1
fi

if ! ls backend/offline/wheels-linux/*cp38*.whl >/dev/null 2>&1; then
  echo "ERROR: offline wheels do not contain cp38 builds"
  echo "Please rebuild backend/offline/wheels-linux with Python 3.8"
  exit 1
fi

echo "[3/7] Install backend deps from offline wheels"
pip install --no-index --find-links=backend/offline/wheels-linux -r backend/requirements.txt

echo "[4/7] Configure systemd backend"
cat >/etc/systemd/system/license-portal-backend.service <<EOF
[Unit]
Description=License Portal Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR/backend
Environment=LOG_BASE_DIR=$LOG_DIR
ExecStart=$APP_DIR/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now license-portal-backend

echo "[5/7] Deploy frontend static files"
if ! command -v nginx >/dev/null 2>&1; then
  echo "ERROR: nginx not found. Please install nginx before offline deployment."
  exit 1
fi
mkdir -p /usr/share/nginx/license-portal
cp -r frontend/dist/* /usr/share/nginx/license-portal/

cat >/etc/nginx/conf.d/license-portal.conf <<'EOF'
server {
  listen 80;
  server_name _;

  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  location / {
    root /usr/share/nginx/license-portal;
    try_files $uri /index.html;
  }
}
EOF

nginx -t
systemctl restart nginx

echo "[6/7] Import fixed-layout license files"
chmod +x deploy/sync_fixed_layout.sh
API_BASE=http://127.0.0.1:8000/api LICENSE_DIR="$LICENSE_DIR" deploy/sync_fixed_layout.sh

echo "[7/7] Verify"
if curl -s http://127.0.0.1:8000/api/health | grep -q "ok"; then
  echo "OK: backend healthy"
else
  echo "WARN: backend may not be ready yet"
fi

echo ""
echo "Done. UI: http://$(hostname -I | awk '{print $1}' || echo '<server-ip>')/"
