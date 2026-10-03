#!/usr/bin/env bash
# Helper: list recording checklist (manual recording on phone is preferred).
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Save clips to: $DIR/audio/"
echo "Update: $DIR/labels.csv (copy from labels_template.csv)"
echo "Target: 20-30 clips; see README.md"
