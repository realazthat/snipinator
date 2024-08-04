#!/bin/bash
# WARNING: This file is auto-generated by snipinator. Do not edit directly.
# SOURCE: `snipinator/examples/example_example.sh.jinja2`.

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail
set +v
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
PS4="${GREEN}$ ${NC}"



# Don't run this in act/GH actions because act doesn't play with with nested
# docker; the paths mess up.
if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
  echo -e "${YELLOW}This script is not meant to be run in GitHub Actions.${NC}"
  exit 0
fi

: ECHO_SNIPPET_START
# SNIPPET_START
# View the template file.
cat "snipinator/examples/EXAMPLE.md.jinja2"

# Use the published images at ghcr.io/realazthat/snipinator.
# /data in the docker image is the working directory, so paths are simpler.
docker run --rm --tty \
  -u "$(id -u):$(id -g)" \
  -v "${PWD}:/data" \
  ghcr.io/realazthat/snipinator:v3.1.0 \
  -t "snipinator/examples/EXAMPLE.md.jinja2" \
  --rm \
  --force \
  --create \
  -o "snipinator/examples/EXAMPLE.generated.md" \
  --chmod-ro \
  --skip-unchanged

# View the generated file.
cat "snipinator/examples/EXAMPLE.generated.md"

# SNIPPET_END
: ECHO_SNIPPET_END
