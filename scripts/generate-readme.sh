#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

# NOTE: Use dev requirements to generate the README because the README uses
# shell() with some tools that we only want to install into dev environment.
VENV_PATH="${PWD}/.cache/scripts/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
TOML=${PROJ_PATH}/pyproject.toml EXTRA=dev \
  DEV_VENV_PATH="${PWD}/.cache/scripts/.venv" \
  TARGET_VENV_PATH="${PWD}/.cache/scripts/.venv" \
  bash "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

python -m snipinator.cli \
  -t "${PROJ_PATH}/snipinator/examples/EXAMPLE.md.jinja2" \
  --rm \
  --force \
  -o "${PROJ_PATH}/snipinator/examples/EXAMPLE.generated.md" \
  --chmod-ro

python -m snipinator.cli \
  -t "${PROJ_PATH}/README.md.jinja2" \
  --rm \
  --force \
  -o "${PROJ_PATH}/README.md" \
  --chmod-ro
