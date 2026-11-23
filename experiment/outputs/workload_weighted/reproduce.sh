#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT=$(CDPATH= cd -- "$HERE/../.." && pwd)
REPO=$(CDPATH= cd -- "$PROJECT/.." && pwd)
PYTHON=${PYTHON:-"$REPO/.venv/bin/python"}
SOURCE=${1:-"$REPO/data/raw"}
"$PYTHON" "$PROJECT/workload_weighted.py" --source "$SOURCE" --output "$HERE"
"$PYTHON" "$PROJECT/verify_weighted.py"
