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

EXAMPLE_MD_JINJA2=$(cat <<EOF
TEST
EOF
)
EXAMPLE_MD_GEN_PATH="${TMP_DIR}/EXAMPLE.generated.md"
EXAMPLE_MD_JINJA2_PATH="${TMP_DIR}/EXAMPLE.md.jinja2"

echo "${EXAMPLE_MD_JINJA2}" > "${EXAMPLE_MD_JINJA2_PATH}"

python -m snipinator.cli \
  --cwd "${TMP_DIR}" \
  -t "${EXAMPLE_MD_JINJA2_PATH}" \
  -o "${EXAMPLE_MD_GEN_PATH}"

echo -m "${GREEN}Successfully ran from inside project${NC}"

cd "${TMP_DIR}"
EXIT_CODE=0
python -m snipinator.cli \
  -t "${EXAMPLE_MD_JINJA2_PATH}" \
  -o "${EXAMPLE_MD_GEN_PATH}" \
  --check || EXIT_CODE=$?

if [[ "${EXIT_CODE}" -eq 0 ]]; then
  echo -e "${RED}Expected to fail from outside project${NC}"
  exit 1
fi
echo -m "${GREEN}Success: failed from outside project${NC}"

echo -e "${GREEN}${BASH_SOURCE[0]}: Tests ran successfully${NC}"
