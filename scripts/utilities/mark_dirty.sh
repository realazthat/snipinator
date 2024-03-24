#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/common.sh"

DIRTY_METHOD=${DIRTY_METHOD:-"xxhash"}

if [[ -z "${TOUCH_FILE:-}" ]]; then
  echo -e "${RED}TOUCH_FILE is not set${NC}"
  [[ $0 == "${BASH_SOURCE[0]}" ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi

if [[ -z "${TOUCH_FILE:-}" ]]; then
  echo -e "${RED}TOUCH_FILE is not set${NC}"
  [[ $0 == "${BASH_SOURCE[0]}" ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi

if [[ -z "${TOML:-}" ]]; then
  echo -e "${RED}TOML is not set${NC}"
  [[ $0 == "${BASH_SOURCE[0]}" ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi

if [[ "${DIRTY_METHOD}" == "stat" ]]; then
  touch "${TOUCH_FILE}"
elif [[ "${DIRTY_METHOD}" == "xxhash" ]]; then
  xxh128sum "${TOML}" > "${TOUCH_FILE}"
else
  echo -e "${RED}DIRTY_METHOD should be either stat or xxhash${NC}"
  [[ $0 == "${BASH_SOURCE[0]}" ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi
