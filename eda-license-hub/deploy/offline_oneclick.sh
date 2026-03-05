#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/license-portal}
LOG_DIR=${LOG_DIR:-/eda/env/license/log}
LICENSE_DIR=${LICENSE_DIR:-/eda/env/license}
RUNTIME_DIR=${RUNTIME_DIR:-$APP_DIR/runtime/miniconda}

cd "$APP_DIR"

if [[ ! -f runtime/Miniconda3-Linux-x86_64.sh ]]; then
  echo "Missing runtime/Miniconda3-Linux-x86_64.sh"
  exit 1
fi

if [[ ! -d backend/offline/wheels-linux ]]; then
  echo "Missing backend/offline/wheels-linux"
  exit 1
fi

if [[ ! -d frontend/dist ]]; then
  echo "Missing frontend/dist"
  exit 1
fi

echo "[1/7] Install embedded Python runtime"
bash runtime/Miniconda3-Linux-x86_64.sh -b -p "$RUNTIME_DIR"

export PATH="$RUNTIME_DIR/bin:$PATH"

echo "[2/7] Create backend venv"
python -m venv backend/.venv
source backend/.venv/bin/activate


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
curl -s http://127.0.0.1:8000/api/health

echo "Done. UI: http://<server-ip>/"
