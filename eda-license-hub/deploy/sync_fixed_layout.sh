#!/usr/bin/env bash
set -euo pipefail

API_BASE=${API_BASE:-http://127.0.0.1:8000/api}
LICENSE_DIR=${LICENSE_DIR:-/eda/env/license}

# Fixed file naming from user convention
FILES=(
  "$LICENSE_DIR/synopsys_lic01.dat"
  "$LICENSE_DIR/synopsys_lic02.dat"
  "$LICENSE_DIR/cadence_lic01.dat"
  "$LICENSE_DIR/cadence_lic02.dat"
  "$LICENSE_DIR/mentor_lic01.dat"
  "$LICENSE_DIR/mentor_lic02.dat"
)

for f in "${FILES[@]}"; do
  if [[ -f "$f" ]]; then
    echo "Import: $f"
    curl -sS -X POST -F "file=@$f" "$API_BASE/license/upload" >/dev/null
  fi
done

echo "Sync done"
