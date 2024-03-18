#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH="${PWD}/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
REQS="${PROJ_PATH}/requirements.txt" source "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

export PYTHONPATH=${PYTHONPATH:-}
export PYTHONPATH=${PYTHONPATH}:${PWD}

# For each sh in snipinator/examples
find snipinator/examples -type f -name "*.sh" -print0 | while IFS= read -r -d '' EXAMPLE; do
  bash "${EXAMPLE}"
  echo -e "${GREEN}${EXAMPLE} ran successfully${NC}"
done

echo -e "${GREEN}${BASH_SOURCE[0]} ran successfully${NC}"
