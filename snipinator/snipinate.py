# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.
"""Python code snippets for markdown files, e.g READMEs, from actual (testable) code."""

import ast
import base64
import html
import json
import logging
import shlex
import subprocess
import sys
import textwrap
from functools import partial
from io import StringIO
from pathlib import Path
from typing import Generator, List, Literal
from xml.dom import minidom

import markupsafe
import pexpect  # type: ignore[import]
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.terminal_theme import MONOKAI
from rich.text import Text
from rich.themes import DEFAULT as DEFAULT_THEME

logger = logging.getLogger(__name__)
DEFAULT_WARNING = '''
WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `{template_file_name}`.
'''


def Snipinate(template_file_name: str,
              template_string: str,
              cwd: Path,
              template_args: dict,
              templates_searchpath: Path | None,
              warning_message: str = DEFAULT_WARNING) -> str:
  """Render the markdown template.

  Args:
      template_file_name (str): File name of the template, used for error
        reporting.
      template_string (str): The content of the template.
      cwd (Path): Current working directory, used as a base for resolving
        relative paths in the template.
      template_args (dict): Any extra values the user wishes to pass to the
        template, e.g. `{'name': 'John'}` if they wish to render variables as
        Jinja2 is capable of.
      templates_searchpath (Path | None): If specified, will use a custom
        FileSystemLoader for Jinja2, with this search path. This is useful for
        inclusion macros, etc. Defaults to None.
      warning_message (str, optional): If specified, the top of the rendered
        markdown will contain this warning. Useful for adding warnings about
        editing the file, since it is generated. Defaults to DEFAULT_WARNING.

  Returns:
      str: Rendered markdown.
  """
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
                decomentify: bool = False,
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        comments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
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
  signature = _Decomentify(signature, decomentify=decomentify)
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
              decomentify: bool = False,
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        comments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
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
  snippet = _Decomentify(snippet, decomentify=decomentify)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def rawsnippet(path: str,
               *,
               escape: bool = False,
               indent: str | int | None = None,
               backtickify: bool | str = False,
               decomentify: bool = False,
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        comments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: The snippet.
  """

  path_ = _CheckPath(path=path, cwd=cwd)
  snippet = path_.read_text()
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  snippet = _Decomentify(snippet, decomentify=decomentify)
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
            decomentify: bool = False,
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        comments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
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
  snippet = _Decomentify(snippet, decomentify=decomentify)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def path(path: str,
         *,
         escape: bool = False,
         indent: str | int | None = None,
         backtickify: bool | str = False,
         decomentify: bool = False,
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        comments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: Just returns the path. If the path doesn't exist,
        it will raise an error.
  """
  _CheckPath(path=path, cwd=cwd)

  if not Path(path).exists():
    raise FileNotFoundError(f'File not found: {json.dumps(path)}')

  path_str = path
  path_str = _Backtickify(path_str, backtickify=backtickify)
  path_str = _Indent(path_str, indent=indent)
  path_str = _Decomentify(path_str, decomentify=decomentify)
  if not escape:
    return markupsafe.Markup(path_str)
  else:
    return path_str


def _ExecuteANSI(cmd: List[str], cwd: Path) -> str:
  return pexpect.spawn(shlex.join(cmd), cwd=str(cwd)).read().decode()


def shell(args: str,
          *,
          escape: bool = False,
          indent: str | int | None = None,
          backtickify: bool | str = False,
          decomentify: bool = False,
          rich: Literal['svg'] | Literal['img+svg'] | Literal['raw'] = 'raw',
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
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        uncomments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
      rich (Literal['svg']|Literal['img+svg']|Literal['raw'], optional): If
        'svg' a raw svg tag will be dumped into the markdown with the colored
        terminal output. Note that your markdown renderer may not support this.
        If 'img+svg' a base64 encoded image will be dumped into the markdown
        with the colored terminal output. If 'raw' the raw terminal output will
        be dumped into the markdown directly. Defaults to 'raw.
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.

  Returns:
      str | markupsafe.Markup: Returns the output of the command.
  """
  if rich in ['svg', 'img+svg']:
    output = _ExecuteANSI(shlex.split(args), cwd=cwd)

    CONSOLE_SVG_FORMAT = """\
    <svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Generated with Rich textualize.io -->
<style>
@font-face {{
font-family: "Fira Code";
src: local("FiraCode-Regular"),
url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
font-style: normal;
font-weight: 400;
}}
@font-face {{
font-family: "Fira Code";
src: local("FiraCode-Bold"),
url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
font-style: bold;
font-weight: 700;
}}

.{unique_id}-matrix {{
font-family: Fira Code, monospace;
font-size: {char_height}px;
line-height: {line_height}px;
font-variant-east-asian: full-width;
}}

.{unique_id}-title {{
font-size: 18px;
font-weight: bold;
font-family: arial;
}}

{styles}
</style>

        <defs>
        <clipPath id="{unique_id}-clip-terminal">
          <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
        </clipPath>
        {lines}
        </defs>

        <g transform="translate({terminal_x}, 0)">
        {backgrounds}
        <g class="{unique_id}-matrix">
        {matrix}
        </g>
        </g>
    </svg>
    """

    def CleanSVG(svg_code):

      # Parse SVG content
      dom = minidom.parseString(svg_code)
      # Get the pretty printed version of the SVG content
      cleaned_svg = dom.toprettyxml(indent='')
      # minidom adds extra lines; remove them
      cleaned_svg = '\n'.join(
          [line for line in cleaned_svg.split('\n') if line.strip()])

      return cleaned_svg

    width = 80
    console = Console(record=True,
                      force_terminal=True,
                      force_interactive=True,
                      width=width,
                      theme=DEFAULT_THEME,
                      file=StringIO())
    text = Text.from_ansi(output)
    console.print(f'${args}')
    console.print(text)
    console.height = len(text.wrap(console, width=width))
    svg = console.export_svg(theme=MONOKAI, code_format=CONSOLE_SVG_FORMAT)
    svg = CleanSVG(svg)

    print('svg:', svg)
    if rich == 'svg':
      output = svg
    elif rich == 'img+svg':
      output = ('<img src="data:image/svg+xml;base64,' +
                base64.b64encode(svg.encode()).decode() + '"/>')
    else:
      raise ValueError(f'Unsupported rich format: {json.dumps(rich)}')
  else:
    result = subprocess.run(shlex.split(args),
                            cwd=cwd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            check=True)
    output = f'${args}\n{result.stdout}'
  output = _Backtickify(output, backtickify=backtickify)
  output = _Indent(output, indent=indent)
  output = _Decomentify(output, decomentify=decomentify)
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
) -> Generator[str, None, None]:
  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
    yield node.name
    return
  elif isinstance(node, ast.Assign):
    for target in node.targets:
      if isinstance(target, ast.Name):
        id: str = target.id
        yield id
    return
  raise ValueError(f'Unsupported node type: {type(node)}')


def _FindMatchingChildNodes(*, parent: ast.AST,
                            symbol_part: str) -> Generator[ast.AST, None, None]:
  child_node: ast.AST
  for child_node in ast.iter_child_nodes(parent):
    if not isinstance(
        child_node,
        (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign)):
      continue
    names = _GetNodeNames(child_node)
    if symbol_part in names:
      yield child_node


def _FindTargetNodes(*, start: ast.AST,
                     symbol_parts: List[str]) -> Generator[ast.AST, None, None]:
  candidates = [start]
  for symbol_part in symbol_parts:
    next_candidates = []
    candidate: ast.AST
    for candidate in candidates:
      matching_node: ast.AST
      for matching_node in _FindMatchingChildNodes(parent=candidate,
                                                   symbol_part=symbol_part):
        next_candidates.append(matching_node)
    candidates = next_candidates
  yield from candidates


def _FindTargetNode(*, start: ast.AST,
                    symbol_parts: List[str]) -> ast.AST | None:
  for target_node in _FindTargetNodes(start=start, symbol_parts=symbol_parts):
    return target_node
  return None


def _DumpNode(*, source: str, node: ast.AST) -> str:
  start_line_index = node.lineno - 1
  end_line_index = _GetEOLIndex(node)
  code = source.splitlines()[start_line_index:end_line_index + 1]
  return '\n'.join(code)


def _GetSymbolSource(*, path: Path, symbol: str) -> str:
  symbol_parts = symbol.split('.')
  try:
    source = path.read_text()
    tree = ast.parse(source)
    nodes = list(_FindTargetNodes(start=tree, symbol_parts=symbol_parts))
    for node in nodes:
      return _DumpNode(source=source, node=node)
    raise ValueError(
        f'Symbol {json.dumps(symbol)} not found in {json.dumps(str(path))}')
  except Exception as e:
    raise ValueError(
        f'Error getting source for {json.dumps(symbol)} in {json.dumps(str(path))}: {json.dumps(str(e))}'
    ) from e


def _GetClassDocstringEndIndex(class_node: ast.ClassDef) -> int:
  if not class_node.body:
    return class_node.lineno - 1
  first_member_line = class_node.body[0].lineno
  first_member_line_index = first_member_line - 1
  return first_member_line_index - 1


def _GetEOLIndex(node: ast.AST) -> int:

  if hasattr(node, 'end_lineno') and node.end_lineno is not None:
    return node.end_lineno - 1

  lineno = getattr(node, 'lineno', None)
  name = getattr(node, 'name', 'N/A')
  raise ValueError(
      f'end_lineno not found for {json.dumps(name)} of type {type(node)} defined at line {lineno}, this can happen in Python < 3.8.0. sys.version_info: {sys.version_info}.'
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


def _EndIndex(target_node: ast.AST) -> int | None:
  if isinstance(target_node, ast.ClassDef):
    return _GetClassDocstringEndIndex(target_node)
  elif isinstance(target_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
    return _FirstNonDocstringLineIndex(target_node)
  return None


def _GetSymbolSignature(source: str, path: str, symbol: str) -> str:
  try:
    tree = ast.parse(source, filename=Path(path).name)

    target_node = _FindTargetNode(start=tree, symbol_parts=symbol.split('.'))
    if target_node is None:
      raise ValueError(
          f'Symbol {json.dumps(symbol)} not found in {json.dumps(str(path))}')

    start_line_index = target_node.lineno - 1
    end_line_index = _EndIndex(target_node)
    if end_line_index is None:
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


def _Decomentify(text: str, *, decomentify: bool) -> str:
  if decomentify:
    return '-->' + text + '<!--'
  else:
    return text
