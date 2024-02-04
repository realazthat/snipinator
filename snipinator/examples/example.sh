#!/bin/bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail


# HELP START
python -m snipinator.cli --help
# HELP END

# EXAMPLE START
python -m snipinator.cli \
  -t "snipinator/examples/EXAMPLE.md.jinja2" \
  -o "snipinator/examples/EXAMPLE.md" \
  --chmod 555
# EXAMPLE END
