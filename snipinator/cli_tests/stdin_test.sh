#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'


TMP_DIR=$(mktemp -d)
ORIGINAL_PWD="${PWD}"

function delete_tmp_dir {
  cd "${ORIGINAL_PWD}"
  rm -rf "${TMP_DIR}"
}
trap delete_tmp_dir EXIT



TEMPLATE=$(cat <<EOF

{{ 'TEST' }}
EOF
)
echo "${TEMPLATE}" > "${TMP_DIR}/EXAMPLE.md.jinja2"


EXPECTED_OUTPUT=$(cat <<'EOF'
<!--

WARNING: This file is auto-generated by snipinator. Do not edit directly.
SOURCE: `-`.

-->

TEST

EOF
)
echo "${EXPECTED_OUTPUT}" > "${TMP_DIR}/EXAMPLE.expected.md"
# FAIL HARD if file has CRLF line endings
if grep -q $'\r' "${TMP_DIR}/EXAMPLE.expected.md"; then
  echo -e "${RED}File has CRLF line endings${NC}"
  exit 1
fi

cat "${TMP_DIR}/EXAMPLE.md.jinja2" \
  | python -m snipinator.cli -t '-' > "${TMP_DIR}/EXAMPLE.generated.md"

# Check the contents of the generated file versus the expected output
git diff --no-index --exit-code \
  "${TMP_DIR}/EXAMPLE.expected.md" \
  "${TMP_DIR}/EXAMPLE.generated.md"
echo -e "${GREEN}Successfully generated expected output${NC}"



echo -e "${GREEN}${BASH_SOURCE[0]}: All tests passed${NC}"