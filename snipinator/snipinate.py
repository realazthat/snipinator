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
import os
import re
import subprocess
import sys
import textwrap
from functools import partial
from io import StringIO
from pathlib import Path
from typing import Generator, List, NamedTuple, Optional, Set, Union

import markupsafe
import pexpect  # type: ignore[import]
import yaml
from defusedxml import minidom  # type: ignore[import]
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
from rich.console import Console
from rich.terminal_theme import MONOKAI
from rich.text import Text
from rich.themes import DEFAULT as DEFAULT_THEME
from typing_extensions import Literal

logger = logging.getLogger(__name__)


class BlockCommentStyle(NamedTuple):
  open: str
  close: str


class LineCommentStyle(NamedTuple):
  line: str


def _Comment(text: str, style: Union[BlockCommentStyle,
                                     LineCommentStyle]) -> str:
  if isinstance(style, BlockCommentStyle):
    open = style.open
    close = style.close
    return f'{open}\n{text}\n{close}\n'
  elif isinstance(style, LineCommentStyle):
    comment = style.line
    return '\n'.join([f'{comment} {line}' for line in text.split('\n')])
  else:
    return ''


def Snipinate(template_file_name: Union[Path, Literal['-']],
              template_string: str,
              cwd: Path,
              template_args: dict,
              templates_searchpath: Optional[Path],
              block_comment: BlockCommentStyle,
              warning_header: str,
              artifact_path: Path,
              output_base_path: Path,
              skip_unchanged: bool = False) -> str:
  """Render the markdown template.

  Args:
      template_file_name (str): File name of the template, used for error
        reporting. Can be '-' to indicate stdin. Otherwise should be a path
        relative to `cwd`. Does not have to exist. Will be used as a hint
        as to where to output embedded files, such as images, etc.
      template_string (str): The content of the template.
      cwd (Path): Current working directory, used as a base for resolving
        relative paths in the template.
      template_args (dict): Any extra values the user wishes to pass to the
        template, e.g. `{'name': 'John'}` if they wish to render variables as
        Jinja2 is capable of.
      templates_searchpath (Path, optional): If specified, will use a custom
        FileSystemLoader for Jinja2, with this search path. This is useful for
        inclusion macros, etc. Defaults to None.
      warning_message (str, optional): If specified, the top of the rendered
        markdown will contain this warning. Useful for adding warnings about
        editing the file, since it is generated. Defaults to DEFAULT_WARNING.
      artifact_path (Path): If specified, will use this as the base path for any
        artifacts that are written to disk.
      output_base_path (Path): If specified, will use this as the base path the
        output file is relative to, used to construct the relative paths in the
        README to the artifacts.
      skip_unchanged: If True, will skip writing any files (e.g SVGs) if the the
        same as the existing file. Defaults to False.

  Returns:
      str: Rendered markdown.
  """
  try:
    warning_header = warning_header.format(
        template_file_name=template_file_name)

    loader: Optional[FileSystemLoader] = None
    if templates_searchpath is not None:
      loader = FileSystemLoader(templates_searchpath)
    # TODO: Set newline_sequence. comment_start_string, comment_end_string,
    # line_comment_prefix, autoescape?
    env = Environment(loader=loader,
                      autoescape=True,
                      keep_trailing_newline=True)

    # This is the context that will be passed to the Jinja2 functions, if they
    # need access to more global state.
    ctx = _Context(cwd=cwd,
                   template_file_name=template_file_name,
                   artifact_path=artifact_path,
                   output_base_path=output_base_path,
                   written_files=set(),
                   block_comment=block_comment,
                   skip_unchanged=skip_unchanged)
    env.globals['pysignature'] = partial(pysignature, _ctx=ctx)
    env.globals['pysnippet'] = partial(pysnippet, _ctx=ctx)
    env.globals['rawsnippet'] = partial(rawsnippet, _ctx=ctx)
    env.globals['snippet'] = partial(snippet, _ctx=ctx)
    env.globals['path'] = partial(path, _ctx=ctx)
    env.globals['shell'] = partial(shell, _ctx=ctx)

    template_ = env.from_string(template_string)
    rendered = template_.render(**template_args)
    return warning_header + rendered
  except TemplateSyntaxError as e:
    print(f'Error: {json.dumps(str(e))}', file=sys.stderr)
    print('template_file_name:', template_file_name, file=sys.stderr)
    print('e.filename', e.filename, file=sys.stderr)
    print('e.lineno', e.lineno, file=sys.stderr)
    print('e.name', e.name, file=sys.stderr)
    raise
  except Exception as e:
    print(f'Error: {json.dumps(str(e))}', file=sys.stderr)
    print('template_file_name:', template_file_name, file=sys.stderr)
    print('cwd:', cwd, file=sys.stderr)
    print('template_args:', template_args, file=sys.stderr)
    print('templates_searchpath:', templates_searchpath, file=sys.stderr)
    raise


class _Context(NamedTuple):
  """Private context for the Jinja2 functions."""

  cwd: Path
  artifact_path: Path
  output_base_path: Path
  template_file_name: Union[Path, Literal['-']]
  written_files: Set[Path]
  block_comment: Optional[BlockCommentStyle]
  skip_unchanged: bool


def pysignature(path: str,
                symbol: str,
                *,
                escape: bool = False,
                indent: Union[str, int, None] = None,
                indented: Union[str, int, None] = None,
                backtickify: Union[bool, str] = False,
                decomentify: Union[bool, Literal['nl']] = False,
                _ctx: _Context) -> str:
  """Return the signature of a class or function in a python file.

  Returns the {class,function} signature and the docstring.

  Args:
      path (str): The path to the file.
      symbol (str): The symbol to extract.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (Union[bool, Literal['nl']], optional): Assuming that you will
        be using HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      str: The signature and docstring.
  """
  path_ = _CheckPath(path=path, cwd=_ctx.cwd)
  source = path_.read_text()
  signature = _GetSymbolSignature(source=source, path=str(path_), symbol=symbol)

  signature = _Backtickify(signature, backtickify=backtickify)
  signature = _Indent(signature, indent=indent)
  signature = _Indented(signature, indented=indented)
  signature = _Decomentify(signature, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(signature)
  else:
    return signature


def pysnippet(path: str,
              symbol: Optional[str],
              *,
              escape: bool = False,
              indent: Union[str, int, None] = None,
              indented: Union[str, int, None] = None,
              backtickify: Union[bool, str] = False,
              decomentify: Union[bool, Literal['nl']] = False,
              _ctx: _Context) -> Union[str, markupsafe.Markup]:
  """Return a python snippet, allowing you to specify a class or function.

  Args:
      path (str): The path to the file.
      symbol (Optional[str]): The symbol to extract. If None, the entire file is
        returned. Defaults to None.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (Union[bool, Literal['nl']], optional): Assuming that you will
        be using HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """
  path_ = _CheckPath(path=path, cwd=_ctx.cwd)

  if symbol is None:
    snippet = path_.read_text()
  else:
    snippet = _GetSymbolSource(path=path_, symbol=symbol)

  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  snippet = _Indented(snippet, indented=indented)
  snippet = _Decomentify(snippet, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def rawsnippet(path: str,
               *,
               escape: bool = False,
               indent: Union[str, int, None] = None,
               indented: Union[str, int, None] = None,
               backtickify: Union[bool, str] = False,
               decomentify: Union[bool, Literal['nl']] = False,
               _ctx: _Context) -> Union[str, markupsafe.Markup]:
  """Return an entire file as a snippet.

  Args:
      path (str): The path to the file.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (Union[bool, Literal['nl']], optional): Assuming that you will
        be using HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """

  path_ = _CheckPath(path=path, cwd=_ctx.cwd)
  snippet = path_.read_text()
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  snippet = _Indented(snippet, indented=indented)
  snippet = _Decomentify(snippet, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def snippet(path: str,
            start: str,
            end: str,
            *,
            escape: bool = False,
            indent: Union[str, int, None] = None,
            indented: Union[str, int, None] = None,
            backtickify: Union[bool, str] = False,
            decomentify: Union[bool, Literal['nl']] = False,
            regex: Union[bool, str] = False,
            _ctx: _Context) -> Union[str, markupsafe.Markup]:
  """Returns a _delimited_ snippet from a file.

  Does not return the delimiters themselves.

  Args:
      path (str): The path to the file.
      start (str): A string that indicates the start of the snippet.
      end (str): A string that indicates the end of the snippet.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (Union[bool, Literal['nl']], optional): Assuming that you will
        be using HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      regex (Union[bool, str], optional): If True, `start` and `end` will be
        treated as regular expressions. Optionally, can pass in python regex
        flags separated by `|` characters, e.g "IGNORECASE|MULTILINE". Defaults
        to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """

  path_ = _CheckPath(path=path, cwd=_ctx.cwd)

  full_source = path_.read_text()
  snippet = _ExtractDelimted(name=f'input ({path})',
                             text=full_source,
                             start=start,
                             end=end,
                             regex=regex)
  snippet = _Backtickify(snippet, backtickify=backtickify)
  snippet = _Indent(snippet, indent=indent)
  snippet = _Indented(snippet, indented=indented)
  snippet = _Decomentify(snippet, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(snippet)
  else:
    return snippet


def path(path: str,
         *,
         escape: bool = False,
         indent: Union[str, int, None] = None,
         indented: Union[str, int, None] = None,
         backtickify: Union[bool, str] = False,
         decomentify: Union[bool, Literal['nl']] = False,
         link: Optional[Literal['md', 'html']] = None,
         text: Optional[str] = None,
         _ctx: _Context) -> Union[str, markupsafe.Markup]:
  """Verifies that `path` exists, and just returns `path`.

  Unfortunately, I don't know how to use this inside a link, because the
  formatters will destroy it, and it cannot be put into a code block (as the url
  section of a link in markdown does not allow code blocks).

  Args:
      path (str): The path to verify.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (Union[bool, Literal['nl']], optional): Assuming that you will
        be using HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      link (Literal['md', 'html'], optional): If specified, will
        return a markdown or html link to the path. Defaults to None.
      text (str, optional): If specified, will use this text as the
        return value instead of the path. If used with link, will return this
        text as the link text instead of the path. Defaults to None.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: Just returns the path. If the path doesn't
        exist, it will raise an error.
  """
  _CheckPath(path=path, cwd=_ctx.cwd)

  if not Path(path).exists():
    raise FileNotFoundError(f'File not found: {json.dumps(path)}')

  text_str: str = path if text is None else text
  output: str = text_str

  if link == 'md':
    # TODO: escape text_str for markdown?
    # TODO: urllib.quote() the URL?
    output = f'[{html.escape(text_str, quote=True)}]({html.escape(path, quote=True)})'
  elif link == 'html':
    # TODO: urllib.quote() the URL?
    output = f'<a href="{html.escape(path, quote=True)}">{html.escape(text_str, quote=True)}</a>'
  elif link is None:
    output = text_str
  output = _Backtickify(output, backtickify=backtickify)
  output = _Indent(output, indent=indent)
  output = _Indented(output, indented=indented)
  output = _Decomentify(output, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(output)
  else:
    return output


def _ExecuteANSI(args: str, cwd: Path, term: Optional[str], rows: int,
                 cols: int) -> str:
  env = os.environ.copy()
  if term is not None:
    env['TERM'] = term
  pty = pexpect.spawn(
      args,
      cwd=str(cwd),
      env=env,  # type: ignore
      dimensions=(rows, cols))
  output: str = pty.read().decode()
  returncode = pty.wait()
  if returncode != 0:
    raise Exception(f'Command failed: {json.dumps(args)}'
                    f'\n  exit code: {returncode}'
                    f'\n  output: {output}'
                    f'\n  cwd: {cwd}'
                    f'\n  env:\n{textwrap.indent(yaml.safe_dump(env), "    ")}')

  return output


def _GetTerminalSVG(args: str,
                    terminal_output: str,
                    cols: int,
                    include_args: bool,
                    bg_color: Optional[str] = None) -> str:

  CONSOLE_SVG_FORMAT = """\
    <svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Generated with Rich textualize.io -->
        <rect width="100%" height="100%" fill="{bg_color}"/>
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
  if bg_color is None:
    # Make it transparent
    bg_color = 'transparent'

  CONSOLE_SVG_FORMAT = CONSOLE_SVG_FORMAT.replace('{bg_color}', bg_color)

  def CleanSVG(svg_code):
    # Parse SVG content
    dom = minidom.parseString(svg_code)
    # Get the pretty printed version of the SVG content
    cleaned_svg = dom.toprettyxml(indent='')
    # minidom adds extra lines; remove them
    cleaned_svg = '\n'.join(
        [line for line in cleaned_svg.split('\n') if line.strip()])

    return cleaned_svg

  console = Console(record=True,
                    force_terminal=True,
                    force_interactive=True,
                    width=cols,
                    theme=DEFAULT_THEME,
                    file=StringIO())
  text = Text.from_ansi(terminal_output)
  if include_args:
    prefix = '$ '
    console.print(f'{prefix}{args}')
  console.print(text)
  console.height = len(text.wrap(console, width=cols))
  svg = console.export_svg(theme=MONOKAI, code_format=CONSOLE_SVG_FORMAT)
  svg = CleanSVG(svg)
  return svg


def _ExtractDelimted(*, name: str, text: str, start: Optional[str],
                     end: Optional[str], regex: Union[bool, str]) -> str:
  flags = 0
  if isinstance(regex, str):
    for flag in regex.split('|'):
      # Use RegexFlag to get the flag value
      flags |= re.RegexFlag[flag].value
    regex = True

  if start is not None and not regex:
    start_index = text.find(start)
    if start_index == -1:
      raise ValueError(
          f'Start delimiter {json.dumps(start)} not found in {name}')
    start_index += len(start)
    text = text[start_index:]
  elif start is not None and regex:
    start_match = re.search(start, text, flags)
    if start_match is None:
      raise ValueError(
          f'Start delimiter {json.dumps(start)} not found in {name}')
    start_index = start_match.end()
    text = text[start_index:]

  if end is not None and not regex:
    end_index = text.find(end)
    if end_index == -1:
      raise ValueError(f'End delimiter {json.dumps(end)} not found in {name}')
    text = text[:end_index]
  elif end is not None and regex:
    end_match = re.search(end, text, flags)
    if end_match is None:
      raise ValueError(f'End delimiter {json.dumps(end)} not found in {name}')
    end_index = end_match.start()
    text = text[:end_index]
  return text


def _WriteTextArtifact(*, path: Path, text: str, _ctx: _Context):
  if _ctx.skip_unchanged and path.exists():
    existing_text = path.read_text()
    if text == existing_text:
      return
  if not _is_relative_to(path, _ctx.artifact_path):
    raise ValueError(
        f'Path is not relative to artifact_path: {json.dumps(str(path))}, artifact_path: {json.dumps(str(_ctx.artifact_path))}'
    )
  if path in _ctx.written_files:
    raise ValueError(
        f'File already written: {json.dumps(str(path))},'
        ' it appears you are writing to the same file twice in the same template.'
    )
  _ctx.written_files.add(path)

  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text)


def shell(args: str,
          *,
          escape: bool = False,
          indent: Union[str, int, None] = None,
          indented: Union[str, int, None] = None,
          backtickify: Union[bool, str] = False,
          decomentify: Union[bool, Literal['nl']] = False,
          rich: Union[Literal['svg'], Literal['img+b64+svg'], Literal['raw'],
                      str] = 'raw',
          rich_alt: Optional[str] = None,
          rich_bg_color: Optional[str] = None,
          rich_term: Optional[str] = None,
          rich_rows: int = 24,
          rich_cols: int = 80,
          include_args: bool = True,
          start: Optional[str] = None,
          end: Optional[str] = None,
          regex: Union[bool, str] = False,
          _ctx: _Context) -> Union[str, markupsafe.Markup]:
  """Run a shell command and return the output.

  Use at your own risk, this can potentially introduce security vulnerabilities.
  Only use if you know what you are doing. Ensure that no untrusted input can
  be injected into the `args` parameter, or, into anything the command might
  access. If an adversary can control the `args` parameter, they can execute
  arbitrary commands on your system.

  Note: On persistent output colors:

  * I found that the environment variables TERM, COLORTERM and FORCE_COLOR,
    CLI_WIDTH, COLUMNS also influence the outputs for some applications.
  * Also various library versions used in various programs, e.g colorama,
    rich-argparse, Pygments might influence the output.
  * I had to pin all my python packages, and explicitly set TERM, COLORTERM and
    FORCE_COLOR, CLI_WIDTH, COLUMNS to get the output to be consistent across
    two different systems, both using Ubuntu, for a single program.

  Args:
      args (str): The command to run.
      escape (bool, optional): Should use HTML entities escaping? Defaults to
        False.
      indent (Union[str, int, None], optional): Should indent? By how much, or
        with what prefix? Defaults to None.
      indented (Union[str, int, None], optional): Indents every line except the
        first. By how much, or with what prefix? Defaults to None.
      backtickify (Union[bool, str], optional): Should surround with backticks?
        With what language? Defaults to False.
      decomentify (bool, optional): Assuming that you will be using HTML
        comments around this call, setting this to true will add corresponding
        uncomments to uncomment the output. This allows you to have the Jinja2
        call unmolested by markdown formatters, because they will be inside of
        a comment section. Defaults to False.
      rich (Union[Literal['svg'], Literal['img+b64+svg'], Literal['raw'], str],
        optional):
        Optionally outputs colored terminal output as an image.
        * If `rich` is a relative file path that ends with ".svg", the svg will
          be saved to that location and an img tag will be emitted. The path
          will be relative to the template file, which is specified on the
          command line. If the template is from stdin, the path will be relative
          to the current working directory (cwd) which is also specified on the
          command line.
        * If 'svg' a raw svg tag will be dumped into the markdown with the
          colored terminal output. Note that your markdown renderer may not
          support this.
        * If 'img+svg' a base64 encoded image will be dumped into the markdown
          with the colored terminal output.
        * If 'raw' the raw (uncolored) terminal output will be dumped into the
          markdown directly.
        * Defaults to 'raw.
      rich_alt (str, optional): The alt text for the img tag. Defaults
        to None.
      rich_bg_color (str, optional): The background color for the
        terminal output. Valid colors include anything valid for SVG colors. See
        <https://developer.mozilla.org/en-US/docs/Web/CSS/color>. Defaults to
        None (fully transparent).
      rich_term: (str, optional): Sets the TERM env var. Defaults to
        None, which uses whatever the env vars already have.
      rich_rows (int, optional): The number of rows to use for the terminal
        output. Doesn't seem to have much effect. Defaults to 24.
      rich_cols (int, optional): The number of columns to use for the terminal
        output. Defaults to 80.
      include_args (bool, optional): Should include the command that was run in
        the output? Defaults to True.
      start (str, optional): If specified, will return only the text after this
        delimiter. Defaults to None.
      end (str, optional): If specified, will return only the text before this
        delimiter. Defaults to None.
      regex (Union[bool, str], optional): If True, `start` and `end` will be
        treated as regular expressions. Optionally, can pass in python regex
        flags separated by `|` characters, e.g "IGNORECASE|MULTILINE". Defaults
        to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: Returns the output of the command.
  """
  if rich == 'raw':
    # Justification for ignoring bandit/B602:
    # * The user passes the args in, and this is a tool for the user.
    # * Presumably, this is running on the user's machine.
    # * Alternatives: The purpose of this tool is to actually run a command on
    #   the shell on behalf of the user, so there is no getting around this.
    # * The user is responsible for the ensuring that their own inputs cannot
    #   be injected. The documentation (README, docstring) has warning about
    #   the security risks.
    result = subprocess.run(
        args,
        cwd=_ctx.cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        # trunk-ignore(bandit/B602)
        shell=True,
        check=True)
    output = _ExtractDelimted(name='output',
                              text=result.stdout,
                              start=start,
                              end=end,
                              regex=regex)
    if include_args:
      prefix = '$ '
      output = f'{prefix}{args}\n{output}'
    if not output.endswith('\n'):
      output += '\n'
  elif (rich in ['svg', 'img+svg']
        or isinstance(rich, str) and rich.endswith('.svg')):
    output = _ExecuteANSI(args,
                          cwd=_ctx.cwd,
                          term=rich_term,
                          rows=rich_rows,
                          cols=rich_cols)
    output = _ExtractDelimted(name='output',
                              text=output,
                              start=start,
                              end=end,
                              regex=regex)

    svg = _GetTerminalSVG(args=args,
                          terminal_output=output,
                          cols=rich_cols,
                          include_args=include_args,
                          bg_color=rich_bg_color)
    if rich == 'svg':
      output = svg
    elif rich == 'img+svg':
      output = ('<img src="data:image/svg+xml;base64,' +
                base64.b64encode(svg.encode()).decode() + '"/>')
    elif isinstance(rich, str) and rich.endswith('.svg'):
      svg_path = Path(rich)
      if svg_path.is_absolute():
        raise ValueError(
            f'Path is absolute: {json.dumps(str(svg_path))}, it should be relative'
        )
      svg_path = _ctx.artifact_path / svg_path
      output_rel_svg_path = svg_path.relative_to(_ctx.output_base_path)
      svg_path.parent.mkdir(parents=True, exist_ok=True)

      _WriteTextArtifact(path=svg_path, text=svg, _ctx=_ctx)

      alt_attr = ''
      if rich_alt is not None:
        rich_alt_escaped = html.escape(rich_alt, quote=True)
        alt_attr = 'alt="' + rich_alt_escaped + '" '

      output = f'<img src="{str(output_rel_svg_path)}" {alt_attr}/>'
    else:
      raise ValueError(
          f'Unsupported rich format: {json.dumps(rich)} it should'
          ' be "raw", "svg", or "img+svg", or a file path ending with ".svg"')
  else:
    raise ValueError(
        f'Unsupported rich format: {json.dumps(rich)}, it should be "raw",'
        ' "svg", or "img+svg", or a file path ending with ".svg"')

  output = _Backtickify(output, backtickify=backtickify)
  output = _Indent(output, indent=indent)
  output = _Indented(output, indented=indented)
  output = _Decomentify(output, decomentify=decomentify, _ctx=_ctx)
  if not escape:
    return markupsafe.Markup(output)
  else:
    return output


def _is_relative_to(path: Path, other: Path) -> bool:
  """Backport of Path.is_relative_to for Python < 3.9."""
  if sys.version_info < (3, 9):
    absolute_path = path.resolve()
    other_absolute = other.resolve()
    return str(absolute_path).startswith(str(other_absolute))
  else:
    return path.is_relative_to(other)


def _CheckPath(*, path: str, cwd: Path) -> Path:
  path_ = Path(path)

  if path_.is_absolute():
    raise ValueError(
        f'Path is absolute: {json.dumps(path)}, it should be relative')
  path_ = cwd / path_

  if not _is_relative_to(path_, cwd):
    raise ValueError(
        f'Path is not relative to cwd: {json.dumps(path)}, cwd: {json.dumps(str(cwd))}'
    )
  return path_


def _GetNodeNames(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign]
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
                    symbol_parts: List[str]) -> Optional[ast.AST]:
  for target_node in _FindTargetNodes(start=start, symbol_parts=symbol_parts):
    return target_node
  return None


def _GetLineNo(node: ast.AST) -> int:
  """Because lineno is not well typed, hide all access to lineno behind this function."""
  if not hasattr(node, 'lineno'):
    raise AssertionError(f'lineno not found for {node}')
  lineno = getattr(node, 'lineno', None)
  if not isinstance(lineno, int):
    raise AssertionError(f'lineno is not an int for {node}')
  return lineno


def _GetEndLineNo(node: ast.AST) -> Optional[int]:
  """Because end_lineno is not well typed, hide all access to end_lineno behind this function."""
  if not hasattr(node, 'end_lineno'):
    return None
  end_lineno = getattr(node, 'end_lineno', None)
  if not isinstance(end_lineno, int):
    raise AssertionError(f'end_lineno is not an int for {node}')
  return end_lineno


def _DumpNode(*, source: str, node: ast.AST) -> str:
  start_line_index = _GetLineNo(node) - 1
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
  end_line_no: Optional[int] = _GetEndLineNo(node)
  if hasattr(node, 'end_lineno') and end_line_no is not None:
    return end_line_no - 1

  lineno = getattr(node, 'lineno', None)
  name = getattr(node, 'name', 'N/A')
  raise ValueError(
      f'end_lineno not found for {json.dumps(name)} of type {type(node)} defined at line {lineno}, this can happen in Python < 3.8.0. sys.version_info: {sys.version_info}.'
  )


def _FirstNonDocstringLineIndex(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
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


def _EndIndex(target_node: ast.AST) -> Optional[int]:
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

    start_line_index = _GetLineNo(target_node) - 1
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


def _Indent(text: str, *, indent: Union[str, int, None]) -> str:
  if isinstance(indent, int):
    return textwrap.indent(text, ' ' * indent)
  elif isinstance(indent, str):
    return textwrap.indent(text, indent)
  else:
    return text


def _Indented(text: str, *, indented: Union[str, int, None]) -> str:
  if indented is None:
    return text
  indent_str = ' ' * indented if isinstance(indented, int) else indented
  lines = text.splitlines()
  return '\n'.join([lines[0]] + [indent_str + line for line in lines[1:]])


def _CountSequentialBackticks(text: str) -> int:
  """Find the largest number of sequential backticks in the text."""
  for backticks in range(1, len(text)):
    search = '`' * backticks
    if search not in text:
      return backticks - 1
  return 0


def _Backtickify(text: str, *, backtickify: Union[bool, str]) -> str:

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


def _Decomentify(text: str, *, decomentify: Union[bool, Literal['nl']],
                 _ctx: _Context) -> str:
  if decomentify is False:
    return text
  if _ctx.block_comment is None:
    raise Exception('decomentify is set, but no block comment style is set')
  if decomentify == 'nl':
    text = f'\n{text}\n'
  return _ctx.block_comment.close + text + _ctx.block_comment.open
