#!/bin/bash
# WARNING: This file is auto-generated by snipinator. Do not edit directly.
# SOURCE: `snipinator/examples/example_example.sh.jinja2`.


# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail


YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Don't run this in act/GH actions because act doesn't play with with nested
# docker; the paths mess up.
if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
  echo -e "${YELLOW}This script is not meant to be run in GitHub Actions.${NC}"
  exit 0
fi

# SNIPPET_START
docker run --rm --tty \
  -v "${PWD}:/data" \
  ghcr.io/realazthat/snipinator:v1.6.0 --help

docker run --rm --tty \
  -v "${PWD}:/data" \
  ghcr.io/realazthat/snipinator:v1.6.0 \
  -t "snipinator/examples/EXAMPLE.md.jinja2" \
  --rm \
  --force \
  --create \
  -o "snipinator/examples/EXAMPLE.generated.md" \
  --chmod-ro
# SNIPPET_END
