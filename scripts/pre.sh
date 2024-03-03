#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

bash scripts/format.sh
bash scripts/type-check.sh
bash scripts/generate-readme.sh
bash scripts/run-all-examples.sh
bash scripts/run-all-tests.sh
bash scripts/precommit.sh
if [[ -z "${GITHUB_ACTIONS:-}" ]]; then
  bash scripts/act.sh
fi
