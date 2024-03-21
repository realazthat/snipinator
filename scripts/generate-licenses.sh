#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH=".cache/scripts/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
TOML=${PROJ_PATH}/pyproject.toml EXTRA=dev source "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

pip-licenses --python .venv/bin/python --format json --with-authors > "${PROJ_PATH}/deps-licenses.json"
pip-licenses --python .cache/scripts/.venv/bin/python --format json --with-authors > "${PROJ_PATH}/dev-deps-licenses.json"

echo -e "${GREEN}Generated licenses${NC}"
