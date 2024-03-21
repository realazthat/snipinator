# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.

import argparse
from pathlib import Path
from typing import List, Tuple
import tomlkit
from tomlkit.toml_document import TOMLDocument

parser = argparse.ArgumentParser(
    description='Pin the dev requirements in pyproject.toml')
parser.add_argument('--toml',
                    type=Path,
                    required=True,
                    help='Path to the pyproject.toml file')
parser.add_argument(
    '--reqs',
    type=Path,
    required=True,
    help='Path to the generated requirements.txt file (from pip-compile)')
args = parser.parse_args()

pyproject_path: Path = args.toml
requirements_path: Path = args.reqs

pyproject_data: TOMLDocument = tomlkit.loads(pyproject_path.read_text())
lines = requirements_path.read_text().splitlines()


def _StripContinuation(line) -> Tuple[bool, str]:
  line = line.strip()
  if line.endswith('\\'):
    return (True, line[:-1].strip())
  return (False, line)


dev_dependencies: List[str] = []
is_continuation = False
for i in range(len(lines)):
  line = lines[i]
  append_to_last = is_continuation
  is_continuation, stripped_line = _StripContinuation(line)
  if not stripped_line:
    continue
  if stripped_line.startswith('#'):
    continue
  if stripped_line.startswith('--'):
    continue
  if append_to_last:
    dev_dependencies[-1] += stripped_line
  else:
    dev_dependencies.append(stripped_line)

opt_deps = pyproject_data['project']['optional-dependencies']
toml_dev_dependencies = opt_deps['dev']
if sorted(list(toml_dev_dependencies)) == sorted(dev_dependencies):
  print('No changes detected')
  exit(0)

toml_dev_dependencies.clear()
for dep in dev_dependencies:
  toml_dev_dependencies.append(dep)
opt_deps['dev'] = toml_dev_dependencies.multiline(True)

output = tomlkit.dumps(pyproject_data)
if output == pyproject_path.read_text():
  print('No changes detected')
  exit(0)

# Write the updated pyproject.toml back to disk
pyproject_path.write_text(tomlkit.dumps(pyproject_data))
