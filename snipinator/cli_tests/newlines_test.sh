#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

BLUE='\033[0;34m'
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

ALL_NEWLINES="lf crlf cr"

for NL_NAME in ${ALL_NEWLINES}; do
  echo -e "${BLUE}Testing newline: ${NL_NAME}${NC}"
  NL_HEX=""
  if [[ "${NL_NAME}" == "lf" ]]; then
    NL=$'\n'
  elif [[ "${NL_NAME}" == "crlf" ]]; then
    NL=$'\r\n'
  elif [[ "${NL_NAME}" == "cr" ]]; then
    NL=$'\r'
  else
    echo -e "${RED}Unknown newline: ${NL_NAME}${NC}"
    exit 1
  fi

  EXAMPLE_MD_JINJA2=$(cat <<EOF
TEST

EOF
)
  EXAMPLE_MD_GEN_PATH="${TMP_DIR}/${NL_NAME}.generated.md"
  EXAMPLE_MD_JINJA2_PATH="${TMP_DIR}/${NL_NAME}.md.jinja2"

  echo "${EXAMPLE_MD_JINJA2}" > "${EXAMPLE_MD_JINJA2_PATH}"


  python -m snipinator.cli \
    --cwd "${TMP_DIR}" \
    -t "${EXAMPLE_MD_JINJA2_PATH}" \
    -o "${EXAMPLE_MD_GEN_PATH}" \
    --output-newline "${NL_NAME}"

  EXAMPLE_MD_GEN_HEX_PATH="${TMP_DIR}/${NL_NAME}.generated.md.hex"
  # Convert to hex, splitting a newline after each byte.
  xxd -p -c 1 "${EXAMPLE_MD_GEN_PATH}" > "${EXAMPLE_MD_GEN_HEX_PATH}"

  # Replace newlines with |
  sed -i "s/\n/Q/g" "${EXAMPLE_MD_GEN_HEX_PATH}"
  NL_HEX=$(echo -n "${NL}" | xxd -p -c 1)

  # If the file does not have NL, then we failed
  if ! grep -q "${NL_HEX}" "${EXAMPLE_MD_GEN_HEX_PATH}"; then
    echo -e "${RED}File does not have newline${NC}"
    exit 1
  fi
done

echo -e "${GREEN}${BASH_SOURCE[0]}: Tests ran successfully${NC}"
