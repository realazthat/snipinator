#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH=".cache/scripts/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
TOML=${PROJ_PATH}/pyproject.toml EXTRA=dev source "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

export FILE="${PROJ_PATH}/pyproject.toml"
export TOUCH_FILE=".cache/scripts/dev-requirements.touch"
if bash "${PROJ_PATH}/scripts/utilities/is_dirty.sh"; then
  echo -e "${BLUE}Generating .cache/scripts/dev-requirements.txt${NC}"

  mkdir -p ".cache/scripts/"
  python -m piptools compile --generate-hashes \
    --extra dev \
    "${PROJ_PATH}/pyproject.toml" \
    -o ".cache/scripts/dev-requirements.txt"
  echo -e "${GREEN}Generated .cache/scripts/dev-requirements.txt${NC}"
else
  echo -e "${GREEN}Requirements .cache/scripts/dev-requirements.txt are up to date${NC}"
fi

export FILE="${PROJ_PATH}/pyproject.toml"
export TOUCH_FILE=".cache/scripts/dev-requirements.touch"
if bash "${PROJ_PATH}/scripts/utilities/is_dirty.sh"; then
  echo -e "${RED}pyproject.toml is dirty, pinning failed${NC}"
  [[ $(realpath "$0"||true) == $(realpath "${BASH_SOURCE[0]}"||true) ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi


python scripts/pin-dev-reqs.py \
  --reqs ".cache/scripts/dev-requirements.txt" \
  --toml "${PROJ_PATH}/pyproject.toml"

if toml-sort "${PROJ_PATH}/pyproject.toml" --check; then
  echo -e "${GREEN}pyproject.toml needs no formatting${NC}"
else
  echo -e "${BLUE}pyproject.toml needs formatting${NC}"
  toml-sort --in-place "${PROJ_PATH}/pyproject.toml"
  echo -e "${GREEN}pyproject.toml formatted${NC}"
fi
if toml-sort "${PROJ_PATH}/pyproject.toml" --check; then
  echo -e "${GREEN}pyproject.toml is formatted${NC}"
else
  echo -e "${RED}pyproject.toml is not formatted${NC}"
  ${EXIT} 1
fi

echo -e "${GREEN}Pinned dev requirements${NC}"
