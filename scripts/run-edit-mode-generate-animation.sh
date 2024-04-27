#!/bin/bash
# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -e -x -v -u -o pipefail

SCRIPT_DIR=$(realpath "$(dirname "${BASH_SOURCE[0]}")")
source "${SCRIPT_DIR}/utilities/common.sh"

VHS_PS1=${VHS_PS1:-}
if [[ -z "${VHS_PS1}" ]]; then
  echo -e "${RED}VHS_PS1 is not set${NC}"
  [[ $0 == "${BASH_SOURCE[0]}" ]] && EXIT="exit" || EXIT="return"
  ${EXIT} 1
fi

# This is meant to run inside the vhs docker container.
apt-get -y install git curl unzip gcc build-essential make zlib1g-dev \
  libssl-dev libffi-dev libncurses5-dev libncursesw5-dev libbz2-dev \
  libreadline-dev libsqlite3-dev liblzma-dev

TMP_DIR=$(mktemp -d)
function cleanup {
  rm -Rf "${TMP_DIR}" || true
}
trap cleanup EXIT

################################################################################


# Copy everything including hidden files, but ignore errors.
cp -a "${PROJ_PATH}/." "${TMP_DIR}" || true

# Make everything writable, because `python -m build` copies everything and then
# deletes it, which is a problem if something is read only.
#
# Skips the dot files.
find "${TMP_DIR}" -type f -not -path '*/.*' -exec chmod 777 {} +


################################################################################
# Install snipinator and run smoke test
cd "${TMP_DIR}"
cp "${PROJ_PATH}/.python-version" .
VENV_PATH="${TMP_DIR}/.venv" source "${PROJ_PATH}/scripts/utilities/ensure-venv.sh"
pip install -U pip

EXIT_CODE=0
python -m snipinator.cli --help || EXIT_CODE=$?
if [[ "${EXIT_CODE}" -eq 0 ]]; then
  echo -e "${RED}Expected snipinator to to fail in a clean environment${NC}"
  exit 1
fi
echo -e "${GREEN}Success: snipinator failed in a clean environment${NC}"

pip install -e "${TMP_DIR}"
echo -e "${GREEN}Success: snipinator installed successfully${NC}"

python -m snipinator.cli --help
python -m snipinator.cli --version
echo -e "${GREEN}Success: snipinator smoke test ran successfully${NC}"

mkdir -p .github
export PS1="${VHS_PS1}"
vhs "${PROJ_PATH}/.github/demo.tape"
cp -f .github/demo.gif "${PROJ_PATH}/.github/demo.gif"

echo -e "${GREEN}${BASH_SOURCE[0]}: Tests ran successfully${NC}"
################################################################################
