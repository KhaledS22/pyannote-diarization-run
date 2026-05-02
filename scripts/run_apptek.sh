#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$ROOT"

if [ "$#" -lt 3 ]; then
  echo "Usage: zsh run_apptek.sh <audio_root> <rttm_root> <output_dir> [python_bin]"
  exit 1
fi

AUDIO_ROOT="$1"
RTTM_ROOT="$2"
OUT_DIR="$3"
PYTHON_BIN="${4:-python}"

MANIFEST_PATH="$OUT_DIR/apptek_manifest.txt"

mkdir -p "$OUT_DIR"

"$PYTHON_BIN" "$PROJECT/build_apptek_manifest.py" \
  --audio-root "$AUDIO_ROOT" \
  --rttm-root "$RTTM_ROOT" \
  --output "$MANIFEST_PATH"

"$PYTHON_BIN" "$PROJECT/run_pyannote_subset.py" \
  --list-file "$MANIFEST_PATH" \
  --out-dir "$OUT_DIR/rttm_outputs" \
  --device cuda

echo
echo "Done."
echo "Manifest: $MANIFEST_PATH"
echo "Outputs:  $OUT_DIR/rttm_outputs"
