#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH=".venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
REQS="${PROJ_PATH}/requirements.txt" source "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

PYTHONPATH=${PYTHONPATH:-}
export PYTHONPATH="${PROJ_PATH}:${PYTHONPATH}"

python -m snipinator.cli \
  -t "${PROJ_PATH}/snipinator/examples/EXAMPLE.md.jinja2" \
  --rm \
  -o "${PROJ_PATH}/snipinator/examples/EXAMPLE.generated.md" \
  --chmod 555

python -m snipinator.cli \
  -t "${PROJ_PATH}/README.md.jinja2" \
  --rm \
  -o "${PROJ_PATH}/README.md" \
  --chmod 555
