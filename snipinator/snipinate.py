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
import subprocess
import sys
import textwrap
from functools import partial
from pathlib import Path
from typing import List

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
    env.globals['pysignature'] = partial(pysignature, cwd=cwd)
    env.globals['pysnippet'] = partial(pysnippet, cwd=cwd)
    env.globals['rawsnippet'] = partial(rawsnippet, cwd=cwd)
    env.globals['snippet'] = partial(snippet, cwd=cwd)
    env.globals['path'] = partial(path, cwd=cwd)
    env.globals['shell'] = partial(shell, cwd=cwd)

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


def pysignature(path: str,
                symbol: str,
                *,
                escape: bool = False,
                indent: str | int | None = None,
                backtickify: bool | str = False,
                cwd: Path) -> str:
  """Return the signature of a class or function in a python file.

  Returns the {class,function} signature and the docstring.

  Args:
      path (str): The path to the file.
      symbol (str): The symbol to extract.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str: The signature and docstring.
  """
  path_ = _CheckPath(path=path, cwd=cwd)
  source = path_.read_text()
  signature = _GetSymbolSignature(source=source, path=str(path_), symbol=symbol)

  signature = _Backtickify(signature, backtickify=backtickify)
  signature = _Indent(signature, indent=indent)
  if not escape:
    return markupsafe.Markup(signature)
  else:
    return signature


def pysnippet(path: str,
              symbol: str | None,
              *,
              escape: bool = False,
              indent: str | int | None = None,
              backtickify: bool | str = False,
              cwd: Path) -> str | markupsafe.Markup:
  """Return a python snippet, allowing you to specify a class or function.

  Args:
      path (str): The path to the file.
      symbol (str | None): The symbol to extract. If None, the entire file is
        returned. Defaults to None.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: The snippet.
  """
  path_ = _CheckPath(path=path, cwd=cwd)

  if symbol is None:
    snippet = path_.read_text()
  else:
    snippet = _GetSymbolSource(path=path_, symbol=symbol)

  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def rawsnippet(path: str,
               *,
               escape: bool = False,
               indent: str | int | None = None,
               backtickify: bool | str = False,
               cwd: Path) -> str | markupsafe.Markup:
  """Return an entire file as a snippet.

  Args:
      path (str): The path to the file.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: The snippet.
  """

  path_ = _CheckPath(path=path, cwd=cwd)
  snippet = path_.read_text()
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def snippet(path: str,
            start: str,
            end: str,
            *,
            escape: bool = False,
            indent: str | int | None = None,
            backtickify: bool | str = False,
            cwd: Path) -> str | markupsafe.Markup:
  """Returns a _delimited_ snippet from a file.

  Does not return the delimeters themselves.

  Args:
      path (str): The path to the file.
      start (str): A string that indicates the start of the snippet.
      end (str): A string that indicates the end of the snippet.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: The snippet.
  """

  path_ = _CheckPath(path=path, cwd=cwd)

  full_source = path_.read_text()

  snippet_start = full_source.find(start)
  snippet_end = full_source.find(end)
  if snippet_start == -1:
    raise ValueError(
        f'Searched for {json.dumps(start)} in {json.dumps(path)} but not found')
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


def path(path: str,
         *,
         escape: bool = False,
         indent: str | int | None = None,
         backtickify: bool | str = False,
         cwd: Path) -> str | markupsafe.Markup:
  """Verifies that `path` exists, and just returns `path`.

  Unfortunately, I don't know how to use this inside a link, because the
  formatters will destroy it, and it cannot be put into a code block (as the url
  section of a link in markdown does not allow code blocks).

  Args:
      path (str): The path to verify.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: Just returns the path. If the path doesn't exist,
        it will raise an error.
  """
  _CheckPath(path=path, cwd=cwd)

  path_str = path
  path_str = _Backtickify(path_str, backtickify=backtickify)
  path_str = _Indent(path_str, indent=indent)
  if not escape:
    return markupsafe.Markup(path_str)
  else:
    return path_str


def shell(args: str,
          *,
          escape: bool = False,
          indent: str | int | None = None,
          backtickify: bool | str = False,
          cwd: Path) -> str | markupsafe.Markup:
  """Run a shell command and return the output.

  Use at your own risk, this can potentially introduce security vulnerabilities.
  Only use if you know what you are doing.

  Args:
      args (str): The command to run.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (str | int | None, optional): Should indent? By how much, or with
        what prefix? Defaults to None.
      backtickify (bool | str, optional): Should surround with backticks? With
        what language? Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: _description_
  """

  result = subprocess.run(args,
                          cwd=cwd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True,
                          shell=True)

  output = f'${args}\n{result.stdout}'
  output = _Backtickify(output, backtickify=backtickify)
  output = _Indent(output, indent=indent)
  if not escape:
    return markupsafe.Markup(output)
  else:
    return output


def _CheckPath(*, path: str, cwd: Path) -> Path:
  path_ = Path(path)

  if path_.is_absolute():
    raise ValueError(
        f'Path is absolute: {json.dumps(path)}, it should be relative')
  path_ = cwd / path_

  if not path_.is_relative_to(cwd):
    raise ValueError(
        f'Path is not relative to cwd: {json.dumps(path)}, cwd: {json.dumps(str(cwd))}'
    )
  return path_


def _GetNodeNames(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Assign
) -> List[str]:
  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
    return [node.name]
  elif isinstance(node, ast.Assign):
    names = []
    for target in node.targets:
      if isinstance(target, ast.Name):
        id: str = target.id
        names.append(id)
    return names
  raise ValueError(f'Unsupported node type: {type(node)}')


def _GetSymbolSource(*, path: Path, symbol: str) -> str:
  try:
    source = path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
      if not isinstance(
          node,
          (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign)):
        continue
      names = _GetNodeNames(node)
      if symbol not in names:
        continue

      # Use the ast module to extract the line numbers and get the source code
      start_line_index = node.lineno - 1
      end_line_index = _GetEOLIndex(node)
      code = source.splitlines()[start_line_index:end_line_index + 1]
      return '\n'.join(code)
    raise ValueError(
        f'Symbol {json.dumps(symbol)} not found in {json.dumps(str(path))}')
  except Exception as e:
    raise ValueError(
        f'Error getting source for {json.dumps(symbol)} in {json.dumps(str(path))}: {json.dumps(str(e))}'
    ) from e


def _FindTargetNode(node: ast.AST, path_parts: List[str]) -> ast.AST | None:
  for child in ast.iter_child_nodes(node):
    if not isinstance(child,
                      (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
      continue
    name = child.name
    if name == path_parts[0]:
      if len(path_parts) == 1:
        return child
      else:
        return _FindTargetNode(child, path_parts[1:])
  return None


def _GetClassDocstringEndIndex(class_node: ast.ClassDef) -> int:
  if not class_node.body:
    return class_node.lineno - 1
  first_member_line = class_node.body[0].lineno
  first_member_line_index = first_member_line - 1
  return first_member_line_index - 1


def _GetEOLIndex(node: ast.AST) -> int:
  if hasattr(node, 'end_lineno') and node.end_lineno is not None:
    return node.end_lineno - 1
  name = getattr(node, 'name', 'N/A')
  raise ValueError(
      f'end_lineno not found for {json.dumps(name)} of type {type(node)} defined at line {node.lineno}, this can happen in Python < 3.8.0. sys.version_info: {sys.version_info}.'
  )


def _FirstNonDocstringLineIndex(
    node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
  """Get the index of the first non-docstring line in the function definition.

  Note: This returns line _index_ which is zero based. AST returns line number.
  """
  if not node.body:
    return _GetEOLIndex(node)
  first_node = node.body[0]
  if isinstance(first_node, ast.Expr) and isinstance(first_node.value,
                                                     (ast.Constant)):
    if len(node.body) >= 2:
      return node.body[1].lineno - 1
    try:
      return _GetEOLIndex(first_node)
    except ValueError:
      return _GetEOLIndex(node)
  else:
    return first_node.lineno - 1


def _GetSymbolSignature(source: str, path: str, symbol: str) -> str:
  try:
    tree = ast.parse(source, filename=Path(path).name)

    path_components = symbol.split('.')
    target_node = _FindTargetNode(tree, path_components)
    if target_node is None:
      raise ValueError(
          f'Symbol {json.dumps(symbol)} not found in {json.dumps(str(path))}')

    start_line_index = target_node.lineno - 1
    if isinstance(target_node, ast.ClassDef):
      end_line_index = _GetClassDocstringEndIndex(target_node)
    elif isinstance(target_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
      end_line_index = _FirstNonDocstringLineIndex(target_node)
    else:
      raise ValueError(
          f'Unsupported symbol type: {json.dumps(symbol)} of type {type(target_node)} in {json.dumps(str(path))}'
      )

    return '\n'.join(source.splitlines()[start_line_index:end_line_index])
  except Exception as e:
    raise ValueError(
        f'Error getting signature for {json.dumps(symbol)} in {json.dumps(str(path))}: {json.dumps(str(e))}'
    ) from e


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
