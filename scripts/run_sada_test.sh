#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$ROOT"

if [ "$#" -lt 3 ]; then
  echo "Usage: zsh run_sada_test.sh <test_csv> <audio_root> <output_dir> [python_bin]"
  exit 1
fi

TEST_CSV="$1"
AUDIO_ROOT="$2"
OUT_DIR="$3"
PYTHON_BIN="${4:-python}"

MANIFEST_PATH="$OUT_DIR/sada_test_manifest.txt"

mkdir -p "$OUT_DIR"

"$PYTHON_BIN" "$PROJECT/build_sada_test_manifest.py" \
  --test-csv "$TEST_CSV" \
  --audio-root "$AUDIO_ROOT" \
  --output "$MANIFEST_PATH"

"$PYTHON_BIN" "$PROJECT/run_pyannote_subset.py" \
  --list-file "$MANIFEST_PATH" \
  --out-dir "$OUT_DIR/rttm_outputs" \
  --device cuda

echo
echo "Done."
echo "Manifest: $MANIFEST_PATH"
echo "Outputs:  $OUT_DIR/rttm_outputs"
