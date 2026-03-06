#!/usr/bin/env bash
# Build full offline package (runtime + wheels + app)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION="1.3.1"
PACKAGE_NAME="eda-license-hub-offline-v${VERSION}"
BUILD_DIR="build"
TEMP_DIR="${BUILD_DIR}/${PACKAGE_NAME}"

echo "========================================"
echo "Build offline package v${VERSION}"
echo "========================================"

echo "[1/6] Check assets..."
[[ -f runtime/Miniconda3-Linux-x86_64.sh ]] || { echo "Missing runtime/Miniconda3-Linux-x86_64.sh"; exit 1; }
[[ -d backend/offline/wheels-linux ]] || { echo "Missing backend/offline/wheels-linux"; exit 1; }
[[ -n "$(ls -A backend/offline/wheels-linux 2>/dev/null)" ]] || { echo "backend/offline/wheels-linux is empty"; exit 1; }
[[ -d frontend/dist ]] || { echo "Missing frontend/dist"; exit 1; }

# Ensure py38 wheels exist (hard guard)
ls backend/offline/wheels-linux/*cp38*.whl >/dev/null 2>&1 || {
  echo "ERROR: wheels-linux does not contain cp38 wheels."
  echo "Rebuild wheels with Python 3.8 first."
  exit 1
}

echo "[2/6] Prepare temp dir..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "[3/6] Copy project files..."
cp -r backend "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/frontend"
cp -r frontend/dist "$TEMP_DIR/frontend/"
cp -r deploy "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/runtime"
cp runtime/Miniconda3-Linux-x86_64.sh "$TEMP_DIR/runtime/"
cp README.md "$TEMP_DIR/" 2>/dev/null || echo "# EDA License Hub" > "$TEMP_DIR/README.md"

# Clean build artifacts
find "$TEMP_DIR/backend" -type d -name '__pycache__' -prune -exec rm -rf {} + || true
find "$TEMP_DIR/backend" -type f -name '*.pyc' -delete || true
rm -rf "$TEMP_DIR/backend/.venv" || true
rm -f "$TEMP_DIR/backend/eda_license_hub.db" "$TEMP_DIR/backend/data.db" || true

echo "[4/6] Write install guide..."
cat > "$TEMP_DIR/INSTALL_OFFLINE.txt" <<EOF
EDA License Hub Offline Package
Version: v${VERSION}

Contents:
- runtime/Miniconda3-Linux-x86_64.sh
- backend/offline/wheels-linux
- backend/
- frontend/dist
- deploy/

Quick start:
1) Upload package:
   scp ${PACKAGE_NAME}.tar.gz root@<server>:/tmp/
2) Extract:
   cd /tmp && tar -xzf ${PACKAGE_NAME}.tar.gz && cd ${PACKAGE_NAME}
3) Install:
   bash deploy/prepare.sh
   bash deploy/offline_oneclick.sh

Notes:
- Offline installer requires root
- Embedded Python runtime is 3.8
- Wheels are pinned for py38
EOF

echo "[5/6] Normalize scripts..."
find "$TEMP_DIR" -type f -name '*.sh' -exec sed -i 's/\r$//' {} +
chmod +x "$TEMP_DIR"/deploy/*.sh 2>/dev/null || true
chmod +x "$TEMP_DIR"/runtime/*.sh 2>/dev/null || true

echo "[6/6] Create archive..."
mkdir -p "$BUILD_DIR"
(
  cd "$BUILD_DIR"
  tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}/"
  sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"
)

rm -rf "$TEMP_DIR"

echo ""
echo "Done: ${BUILD_DIR}/${PACKAGE_NAME}.tar.gz"
cat "${BUILD_DIR}/${PACKAGE_NAME}.tar.gz.sha256"
