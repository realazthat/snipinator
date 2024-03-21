#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VENV_PATH="${PWD}/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
TOML=${PROJ_PATH}/pyproject.toml EXTRA=prod source "${PROJ_PATH}/scripts/utilities/ensure-reqs.sh"

# Find all files in snipinator that end in _test.py
find snipinator -name "*_test.py" -print0 | while IFS= read -r -d '' TEST_FILE; do
  # Turn path into a python module name, e.g path/to/file.py to path.to.file
  TEST_MODULE=$(echo "${TEST_FILE}" | sed -e "s/^\.\///" -e "s/\.py$//" -e "s/\//\./g")
  echo -e "${YELLOW}Running ${TEST_FILE}${NC}"
  python -m "${TEST_MODULE}"
  echo -e "${GREEN}${TEST_FILE} ran successfully${NC}"
done

find snipinator -name "*_test.sh" -print0 | while IFS= read -r -d '' TEST_FILE; do
  echo -e "${YELLOW}Running ${TEST_FILE}${NC}"
  bash "${TEST_FILE}"
  echo -e "${GREEN}${TEST_FILE} ran successfully${NC}"
done

echo -e "${GREEN}${BASH_SOURCE[0]} ran successfully${NC}"
