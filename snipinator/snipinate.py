# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.
"""Python code snippets for markdown files, e.g READMEs, from actual (testable) code."""

import ast
import html
import json
import sys
import textwrap
from functools import partial
from pathlib import Path

import markupsafe
from jinja2 import Environment, FileSystemLoader

DEFAULT_WARNING = '''
WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `{template_file_name}`.
'''


def Snipinate(template_file_name: str,
              template_string: str,
              cwd: Path,
              template_args: dict,
              templates_searchpath: Path | None,
              warning_message: str = DEFAULT_WARNING):
  try:
    warning_message = warning_message.format(
        template_file_name=template_file_name)
    if warning_message:
      warning_message = html.escape(warning_message)
      warning_message = f'<!--\n{warning_message}\n-->\n'

    loader: FileSystemLoader | None = None
    if templates_searchpath is not None:
      loader = FileSystemLoader(templates_searchpath)
    env = Environment(loader=loader,
                      autoescape=True,
                      keep_trailing_newline=True)
    # Bind pysnippet_function cwd argument to the current working directory
    env.globals['pysnippet'] = partial(pysnippet_function, cwd=cwd)
    env.globals['rawsnippet'] = partial(rawsnippet_function, cwd=cwd)
    env.globals['snippet'] = partial(snippet_function, cwd=cwd)

    template_ = env.from_string(template_string)
    rendered = template_.render(**template_args)
    return warning_message + rendered
  except Exception as e:
    print(f'Error: {json.dumps(str(e))}', file=sys.stderr)
    print('template_file_name:', template_file_name, file=sys.stderr)
    print('cwd:', cwd, file=sys.stderr)
    print('template_args:', template_args, file=sys.stderr)
    print('templates_searchpath:', templates_searchpath, file=sys.stderr)
    raise


def pysnippet_function(
    path: str | Path,
    symbol: str | None,
    *,
    cwd: Path,
    escape: bool = False,
    indent: str | int | None = None,
    backtickify: bool | str = False) -> str | markupsafe.Markup:
  path = Path(path)

  if path.is_absolute():
    raise ValueError(
        f'Path is absolute: {json.dumps(str(path))}, it should be relative')
  path = cwd / path

  if not path.is_relative_to(cwd):
    raise ValueError(
        f'Path is not relative to cwd: {json.dumps(str(path))}, cwd: {cwd}')

  if not path.exists():
    raise FileNotFoundError(f'File not found: {json.dumps(str(path))}')

  if symbol is None:
    snippet = path.read_text()
  else:
    snippet = _GetSymbolSource(path=path, symbol=symbol)

  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def rawsnippet_function(
    path: str | Path,
    *,
    cwd: Path,
    escape: bool = False,
    indent: str | int | None = None,
    backtickify: bool | str = False) -> str | markupsafe.Markup:
  path = Path(path)

  if path.is_absolute():
    raise ValueError(
        f'Path is absolute: {json.dumps(str(path))}, it should be relative')
  path = cwd / path

  if not path.is_relative_to(cwd):
    raise ValueError(
        f'Path is not relative to cwd: {json.dumps(str(path))}, cwd: {json.dumps(str(cwd))}'
    )

  if not path.exists():
    raise FileNotFoundError(f'File not found: {json.dumps(str(path))}')
  snippet = path.read_text()
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def snippet_function(
    path: str | Path,
    start: str,
    end: str,
    *,
    cwd: Path,
    escape: bool = False,
    indent: str | int | None = None,
    backtickify: bool | str = False) -> str | markupsafe.Markup:
  path = Path(path)

  if path.is_absolute():
    raise ValueError(
        f'Path is absolute: {json.dumps(str(path))}, it should be relative')
  path = cwd / path

  if not path.is_relative_to(cwd):
    raise ValueError(
        f'Path is not relative to cwd: {json.dumps(str(path))}, cwd: {json.dumps(str(cwd))}'
    )

  if not path.exists():
    raise FileNotFoundError(f'File not found: {json.dumps(str(path))}')
  full_source = path.read_text()

  snippet_start = full_source.find(start)
  snippet_end = full_source.find(end)
  if snippet_start == -1:
    raise ValueError(
        f'Searched for {json.dumps(start)} in {json.dumps(str(path))} but not found'
    )
  if snippet_end == -1:
    raise ValueError(
        f'Searched for {json.dumps(end)} in {json.dumps(str(path))} but not found'
    )
  snippet_start += len(start)
  snippet = full_source[snippet_start:snippet_end]
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def _GetSymbolSource(*, path: Path, symbol: str) -> str:
  source = path.read_text()
  tree = ast.parse(source)
  for node in ast.walk(tree):
    # Check if the node is a ClassDef, FunctionDef, or a variable (Assign) and matches the symbol name
    if isinstance(node,
                  (ast.FunctionDef, ast.ClassDef, ast.Assign)) and getattr(
                      node, 'name', None) == symbol:
      # For variables, it's a bit more complex to match the symbol name, as Assign nodes don't have a 'name' attribute
      if isinstance(node, ast.Assign):
        # This will extract variable names from Assign nodes, but note it assumes simple assignments
        # Complex assignments (e.g., tuple unpacking) are not covered in this simplistic approach
        for target in node.targets:
          if isinstance(target, ast.Name) and target.id == symbol:
            break
        else:
          continue

      # Use the ast module to extract the line numbers and get the source code
      start_line = node.lineno
      end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
      code = source.splitlines()[start_line - 1:end_line]
      return '\n'.join(code)
  raise ValueError(
      f'Symbol {json.dumps(symbol)} not found in {json.dumps(str(path))}')


def _Indent(text: str, *, indent: str | int | None) -> str:
  if isinstance(indent, int):
    return textwrap.indent(text, ' ' * indent)
  elif isinstance(indent, str):
    return textwrap.indent(text, indent)
  else:
    return text


def _CountSequentialBackticks(text: str) -> int:
  """Find the largest number of sequential backticks in the text."""
  for backticks in range(1, len(text)):
    search = '`' * backticks
    if search not in text:
      return backticks - 1
  return 0


def _Backtickify(text: str, *, backtickify: bool | str) -> str:

  count = _CountSequentialBackticks(text)
  count += 1
  count = max(3, count)
  bt_str = '`' * count

  if backtickify is True:
    return f'{bt_str}\n{text}\n{bt_str}'
  elif isinstance(backtickify, str):
    return f'{bt_str}{backtickify}\n{text}\n{bt_str}'
  else:
    return text
