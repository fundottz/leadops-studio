#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../data/lead-response-demo"
python3 -m http.server "${1:-8787}"
