# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.
"""CLI: Python code snipinator for markdown files, e.g READMEs, from actual (testable) code."""

import argparse
import html
import io
import json
import shlex
import shutil
import subprocess
import sys
import time
import warnings
from functools import partial
from pathlib import Path
from shutil import get_terminal_size
from typing import Any, BinaryIO, Callable, Dict, List, Optional, TextIO

import colorama
from rich.console import Console
from rich_argparse import RichHelpFormatter  # type: ignore[import]

from . import _build_version
from .snipinate import BlockCommentStyle, Snipinate

_NEWLINE_HELP = (' See '
                 '<https://docs.python.org/3/library/functions.html#open>'
                 ' for more info on the behavior.'
                 ' Defaults to auto, which means the python default is used.')
_DEFAULT_MARKDOWN_WARNING = '''
<!--

WARNING: This file is auto-generated by snipinator. Do not edit directly.
SOURCE: `{template_file_name}`.

-->
'''.strip() + '\n'
_DEFAULT_BLOCK_COMMENT = ['<!--', '-->']

_ARGPARSE_BOOL_CHOICES = ['true', 'false', 'True', 'False', '1', '0']
_ARGPARSE_BOOL_TRUE = ['true', 'True', '1']
_ARGPARSE_BOOL_FALSE = ['false', 'False', '0']


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


def _ChmodSubprocess(path: Path, mode10: int, console: Console, verbose: bool):
  cmd = ['chmod', str(mode10), str(path)]
  if verbose:
    console.print(f'Running: {shlex.join(cmd)}', style='bold blue')
  subprocess.run(cmd, check=True)


def _ChmodTryAll(*, path: Path, mode10: int, console: Console,
                 verbose: bool) -> None:

  chmods: List[Callable[[Path, int, Console], None]]
  chmods = [_ChmodPathlib, partial(_ChmodSubprocess, verbose=verbose)]

  for chmod in chmods:
    try:
      if verbose:
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


def _MakeWritable(path: Path, console: Console, verbose: bool) -> None:

  # Get the current permissions
  original_mode8: str = _GetPermissionOctant8(path=path)
  original_mode10 = int(original_mode8, 8)
  # Add write permissions
  wanted_mode10: int = original_mode10 | 0o222
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
    if verbose:
      console.print(
          f'Changed mode of {path} from {_OctalToRWXStr(original_mode10)} => {_OctalToRWXStr(new_mode10)}',
          style='bold green')


def _MakeReadonly(path: Path, console: Console, verbose: bool) -> None:

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
    if verbose:
      console.print(
          f'Changed mode of {path} from {_OctalToRWXStr(original_mode10)} => {_OctalToRWXStr(new_mode10)}',
          style='bold green')


class _NewlineAction(argparse.Action):

  def __call__(self, parser, namespace, values, option_string=None):
    if values == 'auto':
      newline = None
    elif values == 'lf':
      newline = '\n'
    elif values == 'crlf':
      newline = '\r\n'
    elif values == 'cr':
      newline = '\r'
    else:
      raise argparse.ArgumentTypeError(
          f'Invalid newline value: {json.dumps(values)}.'
          ' Must be one of {auto, lf, crlf, cr}')
    setattr(namespace, self.dest, newline)


def _WriteToBuffer(rendered: str, template_newline: Optional[str],
                   output_newline: Optional[str], buffer_io: BinaryIO):
  with io.StringIO(rendered, newline=template_newline) as rendered_io:
    with io.StringIO(newline=output_newline) as output_io:
      for line in rendered_io:
        output_io.write(line)
      rendered_bytes = output_io.getvalue().encode()
      buffer_io.write(rendered_bytes)


def _WriteToFile(rendered: str, template_newline: Optional[str],
                 output_io: TextIO):
  with io.StringIO(rendered, newline=template_newline) as rendered_io:
    for line in rendered_io:
      output_io.write(line)


def _RemoveOutputPath(output_path: Path, force: bool, console: Console,
                      verbose: bool) -> None:
  try:
    output_path.unlink()
  except PermissionError:
    if not force:
      raise
    _MakeWritable(output_path, console=console, verbose=verbose)
    output_path.unlink()


def _Move(src: Path, dst: Path, force: bool, console: Console,
          verbose: bool) -> None:
  try:
    shutil.move(str(src), str(dst))
  except (PermissionError, FileNotFoundError):
    if not force:
      raise
    _MakeWritable(dst, console=console, verbose=verbose)
    shutil.move(str(src), str(dst))


def _CreateOutputFile(template_newline: Optional[str],
                      output_newline: Optional[str], output_path: Path,
                      rendered: str, console: Console) -> None:

  if template_newline is None and output_newline is None:
    # Simple case, nothing was specified for newlines, use python defaults.
    output_path.write_text(rendered, encoding=None)
  else:
    with output_path.open('w', encoding=None,
                          newline=output_newline) as output_file:
      _WriteToFile(rendered=rendered,
                   template_newline=template_newline,
                   output_io=output_file)


def _SealOutputFile(output_path: Path, chmod: Optional[str], chmod_ro: bool,
                    console: Console, verbose: bool) -> None:
  ############################################################################
  if chmod_ro:
    _MakeReadonly(output_path, console=console, verbose=verbose)
  ############################################################################
  if chmod:
    warnings.warn('The --chmod option is deprecated, use --chmod-ro instead.',
                  DeprecationWarning,
                  stacklevel=2)
    mode8: str = chmod
    mode10: int = int(chmod, 8)
    _ChmodTryAll(path=output_path,
                 mode10=mode10,
                 console=console,
                 verbose=verbose)
    if verbose:
      console.print(f'Changed mode of {output_path} to {mode8}',
                    style='bold green')


def _MakeBackup(output_path: Path, console: Console,
                verbose: bool) -> Optional[Path]:
  if not output_path.exists():
    if verbose:
      console.print(f'No backup made because {output_path} does not exist.',
                    style='bold yellow')
    return None
  backup_path = output_path.with_suffix(output_path.suffix + '.bak')
  if backup_path.exists():
    backup_path.unlink()
  shutil.copy(output_path, backup_path)
  if verbose:
    console.print(f'Backed up {output_path} to {backup_path}', style='bold')
  return backup_path


class _CustomRichHelpFormatter(RichHelpFormatter):

  def __init__(self, *args, **kwargs):
    if kwargs.get('width') is None:
      width, _ = get_terminal_size()
      if width == 0:
        warnings.warn('Terminal width was set to 0, using default width of 80.',
                      RuntimeWarning,
                      stacklevel=0)
        # This is the default in get_terminal_size().
        width = 80
      # This is what HelpFormatter does to the width returned by
      # `get_terminal_size()`.
      width -= 2
      kwargs['width'] = width
    super().__init__(*args, **kwargs)


def main() -> None:
  console = Console(file=sys.stderr)
  args: Optional[argparse.Namespace] = None
  try:
    # Windows<10 requires this.
    colorama.init()

    p = argparse.ArgumentParser(prog=_GetProgramName(),
                                description=__doc__,
                                formatter_class=_CustomRichHelpFormatter)
    p.add_argument('-t',
                   '--template',
                   type=str,
                   required=True,
                   help='Path to the template file. Use "-" for stdin.')
    p.add_argument(
        '--cwd',
        type=Path,
        default=Path.cwd(),
        help='Directory to use as the base for snippet paths in the template.'
        ' Defaults to the current working directory.')
    p.add_argument(
        '-a',
        '--args',
        type=json.loads,
        default={},
        help='JSON string with template arguments.'
        ' Any extra values the user wishes to pass to the template, e.g.'
        " `{'name': 'John'}` if they wish to render variables as Jinja2 is"
        ' capable of. Defaults to {}.')
    p.add_argument(
        '--templates-searchpath',
        type=Path,
        default=None,
        help='Path to the directory with templates for include directives etc.'
        ' Defaults to None, which means nothing can be included using Jinja2\'s'
        ' include directives, which most users won\'t be needing.')
    p.add_argument(
        '-o',
        '--output',
        type=str,
        default='-',
        help='Path to the output file. Use "-" for stdout. Defaults to "-".')
    p.add_argument(
        '--rm',
        action='store_true',
        default=None,
        help='Remove any existing file at the output path, before writing the'
        ' new one; useful if the existing file might be write protected.')
    p.add_argument(
        '--move',
        action='store_true',
        default=None,
        help='Write output to a temporary location,'
        ' then use filesystem move operation to write it to the destination.')
    p.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='Force remove the existing file at the output path, before writing'
        ' the new one; useful if the existing file might be write protected.'
        ' Defaults to False.')
    p.add_argument(
        '--create',
        action='store_true',
        default=False,
        help='Create an empty file at the destination if it does not exist.'
        ' Useful if the file references itself via path() etc. and so therefore'
        ' must exist during rendering. Defaults to False.')
    p.add_argument(
        '--check',
        action='store_true',
        default=False,
        help='Check if the output file is the same as the rendered text, and'
        ' exit with a non-zero status code if it is not. Does not write the'
        ' file. Ignores options that modify the file (e.g --rm and --chmod-ro).'
        ' Useful for CI pipelines. Defaults to False.')
    warning_group = p.add_mutually_exclusive_group(required=False)
    # TODO(realz): Remove in next major release.
    warning_group.add_argument(
        '--warning-message',
        type=str,
        default=None,
        help=
        'Deprecated: Use --warning-header instead. Warning message to include'
        ' in the output file. To prevent accidentally editing generated file.'
        ' Use {template_file_name} to be a standin for the template file name.'
        ' Standard python str.format() will be used to format the message.'
        ' Do not include comment tags in the message; control the comment'
        ' format via --block-comment.')
    warning_group.add_argument(
        '--warning-header',
        type=str,
        default=_DEFAULT_MARKDOWN_WARNING,
        help=
        'Warning header to include in the output file. To prevent accidentally'
        ' editing generated file. Include all necessary comment tags in the'
        ' message. Also escape as necessary; it will be put into the file raw.'
        ' Use {template_file_name} to be a standin for the template file name.'
        ' Standard python str.format() will be used to format the message.'
        ' Defaults to the default warning header.')
    p.add_argument(
        '--block-comment',
        type=str,
        nargs=2,
        default=_DEFAULT_BLOCK_COMMENT,
        help=
        f'The comment tags for comments, for decomentify() function. Defaults to {",".join(map(json.dumps, _DEFAULT_BLOCK_COMMENT))}.'
    )

    chmod_group = p.add_mutually_exclusive_group(required=False)
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
    backup_group = p.add_mutually_exclusive_group()

    backup_group.add_argument(
        '--make-backup',
        choices=_ARGPARSE_BOOL_CHOICES,
        default=None,
        help='Make a backup of the output file before writing'
        ' the new one. Defaults to False.')
    backup_group.add_argument(
        '--make-tmp-backup',
        choices=_ARGPARSE_BOOL_CHOICES,
        default=None,
        help='Make a temporary backup of the output file before'
        ' writing the new one. If snipiniator runs'
        ' successfully, the backup file will be deleted.'
        ' Defaults to True if --make-backup is set to False.')

    p.add_argument('--template-newline',
                   action=_NewlineAction,
                   metavar='{auto,lf,crlf,cr}',
                   default=None,
                   required=False,
                   help=_NEWLINE_HELP)
    p.add_argument('--output-newline',
                   action=_NewlineAction,
                   metavar='{auto,lf,crlf,cr}',
                   default=None,
                   required=False,
                   help=_NEWLINE_HELP)

    p.add_argument('--version',
                   action='version',
                   version=_build_version,
                   help='Show the version and exit.')
    p.add_argument('--verbose',
                   action='store_true',
                   default=False,
                   help='Print more information.')
    args = p.parse_args()

    verbose: bool = args.verbose
    template_newline: Optional[str] = args.template_newline
    output_newline: Optional[str] = args.output_newline
    block_comment = BlockCommentStyle(*args.block_comment)
    warning_header: str
    if args.warning_message is not None:
      warnings.warn(
          'The --warning-message option is deprecated, use --warning-header instead.',
          DeprecationWarning,
          stacklevel=2)
      warning_header = f'<!--\n{html.escape(args.warning_message)}\n-->'
    else:
      warning_header = args.warning_header

    make_backup: bool
    if args.make_backup is None:
      make_backup = False
    else:
      make_backup = args.make_backup in _ARGPARSE_BOOL_TRUE

    make_tmp_backup: bool
    if args.make_tmp_backup is None:
      make_tmp_backup = not make_backup and args.output != '-'
    else:
      make_tmp_backup = args.make_tmp_backup in _ARGPARSE_BOOL_TRUE

    if args.rm and args.output == '-':
      raise ValueError('Cannot use --rm with stdout')
    if args.move and args.output == '-':
      raise ValueError('Cannot use --move with stdout')
    if make_backup and args.output == '-':
      raise ValueError('Cannot use --make-backup true with stdout')
    if make_tmp_backup and args.output == '-':
      raise ValueError('Cannot use --make-tmp-backup true with stdout')
    if args.chmod and args.output == '-':
      raise ValueError('Cannot use --chmod with stdout')
    if args.chmod_ro and args.output == '-':
      raise ValueError('Cannot use --chmod-ro with stdout')
    if args.create and args.output == '-':
      raise ValueError('Cannot use --create with stdout')
    if args.check and args.output == '-':
      raise ValueError('Cannot use --check with stdout')
    ############################################################################
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
      with template_file_path.open('r', encoding=None,
                                   newline=template_newline) as f:
        template_string = f.read()
    else:
      # Template is to be read from stdin.
      if template_newline is None:
        # Simple case, nothing was specified for newlines.
        template_string = sys.stdin.read()
      else:
        template_buffer: bytes = sys.stdin.buffer.read()
        decode_kwargs: Dict[str, Any] = {}
        with io.StringIO(template_buffer.decode(**decode_kwargs),
                         newline=template_newline) as template_io:
          template_string = template_io.read()
    ############################################################################
    if args.create:
      if args.output == '-':
        raise ValueError('Cannot use --create with stdout')
      output_path = Path(args.output)
      if not output_path.exists():
        output_path.touch()
    ############################################################################
    rendered = Snipinate(template_file_name=template_file_name,
                         template_string=template_string,
                         cwd=args.cwd,
                         template_args=args.args,
                         templates_searchpath=args.templates_searchpath,
                         block_comment=block_comment,
                         warning_header=warning_header)
    ############################################################################
    if args.output == '-':
      # Deal with the stdout case.
      if output_newline is not None and template_newline is None:
        # Simple case, nothing was specified for newlines, use python defaults.
        sys.stdout.write(rendered)
        sys.exit(0)
        return
      else:
        # Transfer the text from the rendered string to stdout, with the
        # specified newlines.
        if output_newline is None:
          _WriteToFile(rendered=rendered,
                       template_newline=template_newline,
                       output_io=sys.stdout)
        else:
          # This seems like the only clean way to write custom newlines to
          # stdout.
          _WriteToBuffer(rendered=rendered,
                         template_newline=template_newline,
                         output_newline=output_newline,
                         buffer_io=sys.stdout.buffer)
        sys.exit(0)
        return
    ############################################################################
    output_path = Path(args.output)
    ############################################################################
    if args.check:
      original_output: Optional[str] = None
      if output_path.exists():
        with output_path.open('r', encoding=None, newline=output_newline) as f:
          original_output = f.read()
      sys.exit(0 if rendered == original_output else 1)
      return
    ############################################################################
    backup_path: Optional[Path] = None
    if make_backup or make_tmp_backup:
      backup_path = _MakeBackup(output_path, console, verbose=verbose)
    ############################################################################
    if args.move:
      tmp_output_path = output_path.with_suffix(output_path.suffix + '.tmp')
      _CreateOutputFile(template_newline=template_newline,
                        output_newline=output_newline,
                        output_path=tmp_output_path,
                        rendered=rendered,
                        console=console)
      if output_path.exists() and args.rm:
        _RemoveOutputPath(output_path,
                          force=args.force,
                          console=console,
                          verbose=verbose)
      _Move(src=tmp_output_path,
            dst=output_path,
            force=args.force,
            console=console,
            verbose=verbose)
    else:
      if output_path.exists() and args.rm:
        _RemoveOutputPath(output_path,
                          force=args.force,
                          console=console,
                          verbose=verbose)
      _CreateOutputFile(template_newline=template_newline,
                        output_newline=output_newline,
                        output_path=output_path,
                        rendered=rendered,
                        console=console)
    ############################################################################
    _SealOutputFile(output_path=output_path,
                    chmod=args.chmod,
                    chmod_ro=args.chmod_ro,
                    console=console,
                    verbose=verbose)
    ############################################################################
    # If everything was succesful, and --make-tmp-backup was specified, delete
    # the backup.
    if make_tmp_backup and backup_path is not None:
      backup_path.unlink()
    ############################################################################
    sys.exit(0)
    return
  except Exception:
    console.print_exception()
    if args:
      console.print('args:', args._get_kwargs(), style='bold red')

    sys.exit(1)
    return


if __name__ == '__main__':
  main()
