#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"


rm -Rf ./.act-project-path
mkdir -p ./.act-project-path
git checkout-index --all --prefix="./.act-project-path/"
# Set .act-project-path to read-only
chmod -R 555 ./.act-project-path
cd ./.act-project-path
go run github.com/nektos/act@c79f59f802673f00911bea93db15b83f5bf3507b push --job build-and-test
