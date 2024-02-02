#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail


# TEMPLATE START
python snipinator.cli --help

python snipinator.cli \
  -t "${PROJ_PATH}/README.md.jinja2" \
  -o "${PROJ_PATH}/README.md" \
  --chmod 555
# TEMPLATE END
