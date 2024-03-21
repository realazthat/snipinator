# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.
"""CLI: Python code snipinator for markdown files, e.g READMEs, from actual (testable) code."""

import argparse
import json
import shlex
import subprocess
import sys
import time
import warnings
from pathlib import Path
from typing import Callable, List, Optional

import colorama
from rich.console import Console
from rich_argparse import RichHelpFormatter  # type: ignore[import]

from . import _build_version
from .snipinate import DEFAULT_WARNING, Snipinate


def _GetProgramName() -> str:
  if __package__:
    # Use __package__ to get the base package name
    base_module_path = __package__
    # Infer the module name from the file path, with assumptions about the structure
    module_name = Path(__file__).stem
    # Construct what might be the intended full module path
    full_module_path = f'{base_module_path}.{module_name}' if base_module_path else module_name
    return f'python -m {full_module_path}'
  else:
    return sys.argv[0]


# chmod the output file
def _OctalStr(*, mode10: int) -> str:
  return f'{mode10:o}'.zfill(3)


def _OctalToRWXStr(mode10: int) -> str:
  # Mapping of octal digits to permission strings
  mapping = {
      '0': '---',
      '1': '--x',
      '2': '-w-',
      '3': '-wx',
      '4': 'r--',
      '5': 'r-x',
      '6': 'rw-',
      '7': 'rwx'
  }

  # Convert each octal digit to its corresponding permission string
  return ''.join(mapping[digit] for digit in _OctalStr(mode10=mode10))


def _OctalToExpressive(mode10: int):
  # Define the basic permission mapping
  mapping = {'7': 'rwx', '5': 'rx', '6': 'rw-', '4': 'r--', '0': '---'}

  # Split the octal permissions into user, group, and others
  user, group, others = [
      mapping.get(digit, '---') for digit in _OctalStr(mode10=mode10)
  ]

  # Format the string in a more expressive way
  return f'u={user},g={group},o={others}'


def _GetPermissionOctant8(*, path: Path) -> str:
  return oct(path.stat().st_mode)[-3:]


def _ChmodPathlib(path: Path, mode10: int, console: Console):
  path.chmod(mode10)


def _ChmodSubprocess(path: Path, mode10: int, console: Console):
  cmd = ['chmod', str(mode10), str(path)]
  console.print(f'Running: {shlex.join(cmd)}', style='bold blue')
  subprocess.run(cmd, check=True)


def _ChmodTryAll(*, path: Path, mode10: int, console: Console) -> None:

  chmods: List[Callable[[Path, int, Console],
                        None]] = [_ChmodPathlib, _ChmodSubprocess]

  for chmod in chmods:
    try:
      console.print(f'Trying chmod method: {chmod}', style='bold blue')
      original_mode8 = _GetPermissionOctant8(path=path)
      if original_mode8 == _OctalStr(mode10=mode10):
        # Already has the correct mode
        return

      chmod(path, mode10, console)
      time.sleep(2)

      new_mode8 = _GetPermissionOctant8(path=path)
      if new_mode8 == _OctalStr(mode10=mode10):
        return
      # Prepare info for exception message.

      # original_mode8 is already computed
      mode8 = _OctalStr(mode10=mode10)
      # new_mode8 is already computed

      original_mode10 = int(original_mode8, 8)
      # mode10 is passed in
      new_mode10 = int(new_mode8, 8)

      original_mode_rwx = _OctalToRWXStr(mode10=original_mode10)
      mode_rwx = _OctalToRWXStr(mode10=mode10)
      new_mode_rwx = _OctalToRWXStr(mode10=new_mode10)

      original_mode_rwx_ = _OctalToExpressive(mode10=original_mode10)
      mode_rwx_ = _OctalToExpressive(mode10=mode10)
      new_mode_rwx_ = _OctalToExpressive(mode10=new_mode10)

      raise ValueError(f'Failed to change mode of {path},'
                       f'\n Wanted: 0o{original_mode8} => 0o{mode8}'
                       f'\n Wanted: {original_mode10} => {mode10}'
                       f'\n Wanted: {original_mode_rwx} => {mode_rwx}'
                       f'\n Wanted: {original_mode_rwx_} => {mode_rwx_}'
                       f'\n Actual: 0o{original_mode8} => 0o{new_mode8}'
                       f'\n Actual: {original_mode10} => {new_mode10}'
                       f'\n Actual: {original_mode_rwx} => {new_mode_rwx}'
                       f'\n Actual: {original_mode_rwx_} => {new_mode_rwx_}')
    except Exception as e:
      console.print(f'Failed to change mode of {path} using {chmod}: {e}',
                    style='bold yellow')
      console.print_exception()
      console.print('Trying next chmod method...', style='bold yellow')
      continue
  raise ValueError(f'Failed to change mode of {path}')


def _MakeReadonly(path: Path, console: Console) -> None:

  # Get the current permissions
  original_mode8: str = _GetPermissionOctant8(path=path)
  original_mode10 = int(original_mode8, 8)
  # Remove write permissions
  wanted_mode10: int = original_mode10 & 0o555
  path.chmod(wanted_mode10)
  new_mode8: str = _GetPermissionOctant8(path=path)
  new_mode10 = int(new_mode8, 8)
  if new_mode10 != wanted_mode10:
    raise ValueError(f'Failed to change mode of {path},'
                     f'\n Wanted: 0o{original_mode8} => 0o{new_mode8}'
                     f'\n Wanted: {original_mode10} => {new_mode10}'
                     f'\n Actual: 0o{original_mode8} => 0o{new_mode8}'
                     f'\n Actual: {original_mode10} => {new_mode10}')
  else:
    console.print(
        f'Changed mode of {path} from {_OctalToRWXStr(original_mode10)} => {_OctalToRWXStr(new_mode10)}',
        style='bold green')


def main() -> int:
  console = Console(file=sys.stderr)
  args: Optional[argparse.Namespace] = None
  try:
    # Windows<10 requires this.
    colorama.init()

    parser = argparse.ArgumentParser(prog=_GetProgramName(),
                                     description=__doc__,
                                     formatter_class=RichHelpFormatter)
    parser.add_argument('-t',
                        '--template',
                        type=str,
                        required=True,
                        help='Path to the template file. Use "-" for stdin.')
    parser.add_argument(
        '--cwd',
        type=Path,
        default=Path.cwd(),
        help='Directory to use as the base for snippet paths in the template.'
        ' Defaults to the current working directory.')
    parser.add_argument(
        '-a',
        '--args',
        type=json.loads,
        default={},
        help='JSON string with template arguments.'
        ' Any extra values the user wishes to pass to the template, e.g.'
        " `{'name': 'John'}` if they wish to render variables as Jinja2 is"
        ' capable of. Defaults to {}.')
    parser.add_argument(
        '--templates-searchpath',
        type=Path,
        default=None,
        help='Path to the directory with templates for include directives etc.'
        ' Defaults to None, which means nothing can be included using Jinja2\'s'
        ' include directives, which most users won\'t be needing.')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='-',
        help='Path to the output file. Use "-" for stdout. Defaults to "-".')
    parser.add_argument(
        '--rm',
        action='store_true',
        default=False,
        help='Remove any existing file at the output path, before writing the new'
        ' one; useful if the existing file might be write protected.')
    parser.add_argument(
        '--check',
        action='store_true',
        default=False,
        help='Check if the output file is the same as the rendered text, and'
        ' exit with a non-zero status code if it is not. Does not write the'
        ' file. Ignores options that modify the file (e.g --rm and --chmod-ro).'
        ' Useful for CI pipelines. Defaults to False.')
    parser.add_argument(
        '--warning-message',
        type=str,
        default=DEFAULT_WARNING,
        help=
        'Warning message to include in the output file. To prevent accidentally'
        ' editing generated file. Defaults to the default warning message.')

    chmod_group = parser.add_mutually_exclusive_group(required=False)
    chmod_group.add_argument(
        '--chmod-ro',
        action='store_true',
        default=False,
        help=
        'Like chmod, but portable between linux and windows, effectively does'
        ' `chmod a-w`. To prevent accidentally editing generated file. Defaults'
        ' to False.')
    chmod_group.add_argument(
        '--chmod',
        type=str,
        default=None,
        help=
        # TODO: Remove this in the next major version (deprecated in 1.0.7).
        'Deprecated: Use --chmod-ro.'
        ' Change the mode (permissions) of the output file, an octant (see chmod'
        ' help for more info) e.g 444 or 555. To prevent accidentally editing'
        ' generated file. Defaults to None.')

    parser.add_argument('--version',
                        action='version',
                        version=_build_version,
                        help='Show the version and exit.')
    args = parser.parse_args()

    if args.rm and args.output == '-':
      raise ValueError('Cannot use --rm with stdout')
    if args.chmod and args.output == '-':
      raise ValueError('Cannot use --chmod with stdout')
    if args.chmod_ro and args.output == '-':
      raise ValueError('Cannot use --chmod-ro with stdout')
    if args.check and args.output == '-':
      raise ValueError('Cannot use --check with stdout')

    template_file_name: str = args.template
    template_string: str
    if template_file_name != '-':
      # If we are not dealing with stdin:

      # Treat it as a path.
      template_file_path = Path(template_file_name)
      if template_file_path.is_absolute():
        # If the path is absolute, we want a relative path for the file name
        # (which is used for debugging and error messages).
        #
        # TODO: Do we want this behavior?
        template_file_name = str(template_file_path.relative_to(args.cwd))
      template_string = template_file_path.read_text()
    else:
      # Template is to be read from stdin.
      template_string = sys.stdin.read()

    rendered = Snipinate(template_file_name=template_file_name,
                         template_string=template_string,
                         cwd=args.cwd,
                         template_args=args.args,
                         templates_searchpath=args.templates_searchpath,
                         warning_message=args.warning_message)

    if args.output == '-':
      sys.stdout.write(rendered)
      return 0
    output_path = Path(args.output)

    if args.check:
      original_output: Optional[str] = None
      if output_path.exists():
        original_output = output_path.read_text(encoding='utf-8')
      return 0 if rendered == original_output else 1

    if output_path.exists() and args.rm:
      output_path.unlink()
    output_path.write_text(rendered, encoding='utf-8')

    ##############################################################################
    if args.chmod_ro:
      _MakeReadonly(output_path, console=console)
    ##############################################################################
    if args.chmod:
      warnings.warn('The --chmod option is deprecated, use --chmod-ro instead.',
                    DeprecationWarning,
                    stacklevel=2)
      mode8: str = args.chmod
      mode10: int = int(args.chmod, 8)
      _ChmodTryAll(path=output_path, mode10=mode10, console=console)
      console.print(f'Changed mode of {output_path} to {mode8}',
                    style='bold green')

    ##############################################################################
    return 0
  except Exception:
    console.print_exception()
    if args:
      console.print('args:', args._get_kwargs(), style='bold red')

    sys.exit(1)


sys.exit(main())
