#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH="${PWD}/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"

export PYTHONPATH=${PYTHONPATH:-}
export PYTHONPATH=${PYTHONPATH}:${PWD}

# Find all files in snipinator that end in _test.py
find snipinator -name "*_test.py" | while read -r TEST_FILE; do
  echo "Running ${TEST_FILE}"
  python "${TEST_FILE}"
done
