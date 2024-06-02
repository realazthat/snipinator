#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail


python -m snipinator.cli --help

# SNIPPET_START
python -m snipinator.cli \
  -t "snipinator/examples/EXAMPLE.md.jinja2" \
  --rm \
  --force \
  --create \
  -o "snipinator/examples/EXAMPLE.generated.md" \
  --chmod-ro
# SNIPPET_END
