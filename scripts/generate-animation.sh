#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH="${PWD}/.cache/scripts/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
TOML=${PROJ_PATH}/pyproject.toml EXTRA=dev \
  DEV_VENV_PATH="${PWD}/.cache/scripts/.venv" \
  TARGET_VENV_PATH="${PWD}/.cache/scripts/.venv" \
  bash "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"


BOLD_GREEN='\033[01;32m'
BOLD_BLUE='\033[01;34m'
VHS_PS1="${BOLD_GREEN}user@machine${NC}:${BOLD_BLUE}/path/to/directory${NC}\$ "
docker run --rm \
  --entrypoint /bin/bash \
  -v "${PWD}:/vhs" \
  -e "VHS_PS1=${VHS_PS1}" \
  ghcr.io/charmbracelet/vhs:v0.7.3-devel-amd64 \
  "scripts/run-edit-mode-generate-animation.sh"
