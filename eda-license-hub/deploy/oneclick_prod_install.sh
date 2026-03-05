#!/usr/bin/env bash
set -euo pipefail

APP_DIR=${APP_DIR:-/opt/license-portal}
LICENSE_DIR=${LICENSE_DIR:-/eda/env/license}
LOG_DIR=${LOG_DIR:-/eda/env/license/log}

echo "[1/6] Prepare app dir: $APP_DIR"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [[ -f ./backend/requirements.txt ]]; then
  echo "Project already extracted in $APP_DIR"
else
  echo "Please extract license-portal-release.tar.gz into $APP_DIR first."
  exit 1
fi

echo "[2/6] Install backend deps"
python3 -m venv backend/.venv
source backend/.venv/bin/activate
if [[ -d backend/wheels ]]; then
  pip install --no-index --find-links=backend/wheels -r backend/requirements.txt
else
  pip install -r backend/requirements.txt
fi

echo "[3/6] Setup systemd backend service"
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

echo "[4/6] Deploy frontend static files"
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

echo "[5/6] Import licenses from fixed naming"
"$APP_DIR/deploy/sync_fixed_layout.sh"

echo "[6/6] Done"
echo "Frontend: http://<server-ip>/"
echo "Backend:  http://<server-ip>/api/health"
