<!--

WARNING: This file is auto-generated by snipinator. Do not edit directly.
SOURCE: `README.md.jinja2`.

-->
<!--







-->

# <div align="center">[![Snipinator][1]][2]</div>

<div align="center">

<!-- Icons from https://lucide.dev/icons/users -->
<!-- Icons from https://lucide.dev/icons/laptop-minimal -->

![**Audience:** Developers][3] ![**Platform:** Linux][4]

</div>

<p align="center">
  <strong>
    <a href="https://github.com/realazthat/snipinator">🏠Home</a>
    &nbsp;&bull;&nbsp;
    <a href="#-features">🎇Features</a>
    &nbsp;&bull;&nbsp;
    <a href="#-installation">🔨Installation</a>
    &nbsp;&bull;&nbsp;
    <a href="#-usage">🚜Usage</a>
    &nbsp;&bull;&nbsp;
    <a href="#-command-line-options">💻CLI</a>
    &nbsp;&bull;&nbsp;
    <a href="#-examples">💡Examples</a>
  </strong>
</p>
<p align="center">
  <strong>
    <a href="#-jinja2-api">🤖Jinja2 API</a>
    &nbsp;&bull;&nbsp;
    <a href="#-requirements">✅Requirements</a>
    &nbsp;&bull;&nbsp;
    <a href="#-gotchas-and-limitations">🚸Gotchas</a>
  </strong>
</p>

<div align="center">

![Top language][5] [![GitHub License][6]][7] [![PyPI - Version][8]][9]
[![Python Version][10]][9]

**CLI to embed (testable) snippets from your codebase into your README**

</div>

---

<div align="center">

|                   | Status                      | Stable                    | Unstable                  |                    |
| ----------------- | --------------------------- | ------------------------- | ------------------------- | ------------------ |
| **[Master][11]**  | [![Build and Test][12]][13] | [![since tagged][14]][15] |                           | ![last commit][16] |
| **[Develop][17]** | [![Build and Test][18]][13] | [![since tagged][19]][20] | [![since tagged][21]][22] | ![last commit][23] |

</div>

<img src=".github/demo.gif" alt="Demo" width="100%">

## ❔ What

What it does: **Snipinator** lets you take a `EXAMPLE.md` template
and include snippets from your (working and tested) codebase.

Turn this ([./snipinator/examples/EXAMPLE.md.jinja2](./snipinator/examples/EXAMPLE.md.jinja2)):

<!---->
```md
# A README

Here is a code snippet:

<!--{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py', decomentify='nl') }}-->

Note that `code.py` has a test:
{{path('./snipinator/examples/code_test.py', link='md')}}.

```
<!---->

Into this ([./snipinator/examples/EXAMPLE.generated.md](./snipinator/examples/EXAMPLE.generated.md)):

<!---->
````md
<!--

WARNING: This file is auto-generated by snipinator. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

<!---->
```py
class MyClass:
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
```
<!---->

Note that `code.py` has a test:
[./snipinator/examples/code_test.py](./snipinator/examples/code_test.py).

````
<!---->

## 🎇 Features

- 📦✅🪄 Supports anything **[Jinja2](https://github.com/pallets/jinja)**
  supports.
- 🥇🐍📜 First-class support for **python** source code.
  - Can include python function signatures, docstrings, entire function source
    code, classes.
- ✂🌐🗂️ Snip from **any source code language**.
  - Put delimiter markers into the code (e.g `# START_SNIPPET`,
    `# END_TEMPLATE`), and use [snippet()](#snippet).
- 🥇🔖📜 First-class support for **Markdown** templates (with `backtickify`,
  `decomentify`).
- 📦🐚🖨️ Can include **[shell](#shell) output**.
  - Supports ANSI colors :heart: :green_heart: :blue_heart: with SVG output
    :camera:.
- ⚙️🔗🗃️ More robust **references/links** to local files using [path()](#path).

## 🔨 Installation

```bash
# Install from pypi (https://pypi.org/project/snipinator/)
pip install snipinator

# Install from git (https://github.com/realazthat/snipinator)
pip install git+https://github.com/realazthat/snipinator.git@v1.4.1
```

## 🚜 Usage

Example template README:
([./snipinator/examples/EXAMPLE.md.jinja2](./snipinator/examples/EXAMPLE.md.jinja2)):

<!---->
```md
# A README

Here is a code snippet:

<!--{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py', decomentify='nl') }}-->

Note that `code.py` has a test:
{{path('./snipinator/examples/code_test.py', link='md')}}.

```
<!---->

Generating the README:

<!---->
````bash
$ python -m snipinator.cli -t snipinator/examples/EXAMPLE.md.jinja2
<!--

WARNING: This file is auto-generated by snipinator. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

<!---->
```py
class MyClass:
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
```
<!---->

Note that `code.py` has a test:
[./snipinator/examples/code_test.py](./snipinator/examples/code_test.py).

````
<!---->

## 💻 Command Line Options

<!---->
<img src="README.help.generated.svg" alt="Output of `python -m snipinator.cli --help`" />
<!---->

## 💡 Examples

- Snipinator's own `README`:
  - Template: [./README.md.jinja2](./README.md.jinja2).
  - Generated: [./README.md](./README.md).
  - Generation script: [./scripts/generate-readme.sh](./scripts/generate-readme.sh).
- Example:
  - Template: [./snipinator/examples/EXAMPLE.md.jinja2](./snipinator/examples/EXAMPLE.md.jinja2).
  - Generated:
    [./snipinator/examples/EXAMPLE.generated.md](./snipinator/examples/EXAMPLE.generated.md).
  - Generation script: [./snipinator/examples/example.sh](./snipinator/examples/example.sh).
- Long example of many features:
  - Template:
    [./snipinator/examples/LONG-EXAMPLE.md.jinja2](./snipinator/examples/LONG-EXAMPLE.md.jinja2).
  - Generated:
    [./snipinator/examples/LONG-EXAMPLE.generated.md](./snipinator/examples/LONG-EXAMPLE.generated.md).
  - Generation script:
    [./snipinator/examples/long-example.sh](./snipinator/examples/long-example.sh).
- Projects using Snipinator:
  - [realazthat/snipinator](https://github.com/realazthat/snipinator), See
    [snipinator/README.md.jinja2](https://github.com/realazthat/snipinator/blob/61cb88593baa099dc375cf5fd40679e4be673fc5/README.md.jinja2).
  - [realazthat/changeguard](https://github.com/realazthat/changeguard), See
    [changeguard/README.md.jinja2](https://github.com/realazthat/changeguard/blob/87d5104b52e651bb9195a3d46dd7f050acbcb534/README.md.jinja2).
  - [realazthat/comfy-catapult](https://github.com/realazthat/comfy-catapult),
    See
    [comfy-catapult/README.md.jinja2](https://github.com/realazthat/comfy-catapult/blob/ff353d48b25fa7b9c35fa11b31d5f2b3039c41c8/README.md.jinja2).
  - [realazthat/comfylowda](https://github.com/realazthat/comfylowda), See
    [comfylowda/README.md.jinja2](https://github.com/realazthat/comfylowda/blob/e01a32c38107aa0b89ccea21c4678d193a186a78/README.md.jinja2).
  - [realazthat/excalidraw-brute-export-cli](https://github.com/realazthat/excalidraw-brute-export-cli),
    See
    [excalidraw-brute-export-cli/README.md.jinja2](https://github.com/realazthat/excalidraw-brute-export-cli/blob/54a3b5b08b644e61c721ab565c576094234c5cc7/README.md.jinja2).

## 🤖 Jinja2 API

The regular Jinja2 v3 template syntax is supported. For more information, see
[Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/).

Additional (Jinja2) functions made available:

### 🐍✂ pysnippet

Used several times in
[./snipinator/examples/LONG-EXAMPLE.md.jinja2](./snipinator/examples/LONG-EXAMPLE.md.jinja2).

Documentation:

<!---->
```py
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
      decomentify (Union[bool, Literal['nl']]): Assuming that you will be using
        HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """
```
<!---->

### 🐍📖 pysignature

Used several times in [./README.md.jinja2](./README.md.jinja2).

Documentation:

<!---->
```py
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
      decomentify (Union[bool, Literal['nl']]): Assuming that you will be using
        HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      str: The signature and docstring.
  """
```
<!---->

### ✂ rawsnippet

Used several times in [./README.md.jinja2](./README.md.jinja2).

Documentation:

<!---->
```py
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
      decomentify (Union[bool, Literal['nl']]): Assuming that you will be using
        HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """

```
<!---->

### ✂ snippet

Example in [./snipinator/examples/LONG-EXAMPLE.md.jinja2](./snipinator/examples/LONG-EXAMPLE.md.jinja2).

Documentation:

<!---->
```py
def snippet(path: str,
            start: str,
            end: str,
            *,
            escape: bool = False,
            indent: Union[str, int, None] = None,
            indented: Union[str, int, None] = None,
            backtickify: Union[bool, str] = False,
            decomentify: Union[bool, Literal['nl']] = False,
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
      decomentify (Union[bool, Literal['nl']]): Assuming that you will be using
        HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: The snippet.
  """

```
<!---->

### 🐚 shell

Used several times in [./README.md.jinja2](./README.md.jinja2).

Documentation:

<!---->
```py
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
      rich (Union[Literal['svg'], Literal['img+b64+svg'], Literal['raw'], str], optional):
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
      rich_alt (Optional[str], optional): The alt text for the img tag. Defaults
        to None.
      rich_bg_color (Optional[str], optional): The background color for the
        terminal output. Valid colors include anything valid for SVG colors. See
        <https://developer.mozilla.org/en-US/docs/Web/CSS/color>. Defaults to
        None (fully transparent).
      rich_term: (Optional[str], optional): Sets the TERM env var. Defaults to
        None, which uses whatever the env vars already have.
      rich_rows (int, optional): The number of rows to use for the terminal
        output. Doesn't seem to have much effect. Defaults to 24.
      rich_cols (int, optional): The number of columns to use for the terminal
        output. Defaults to 80.
      include_args (bool, optional): Should include the command that was run in
        the output? Defaults to True.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: Returns the output of the command.
  """
```
<!---->

### 🌀 path

Used several times in [./README.md.jinja2](./README.md.jinja2).

Documentation:

<!---->
```py
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
      decomentify (Union[bool, Literal['nl']]): Assuming that you will be using
        HTML comments around this call, setting this to true will add
        correspondingcomments to uncomment the output. This allows you to have
        the Jinja2 call unmolested by markdown formatters, because they will be
        inside of a comment section. "nl" adds additional newlines after the
        newline delimiters. Defaults to False.
      link (Optional[Literal['md', 'html']], optional): If specified, will
        return a markdown or html link to the path. Defaults to None.
      text (Optional[str], optional): If specified, will use this text as the
        return value instead of the path. If used with link, will return this
        text as the link text instead of the path. Defaults to None.
      _ctx (_Context): This is used by the system and is not available as an
        argument.

  Returns:
      Union[str, markupsafe.Markup]: Just returns the path. If the path doesn't exist,
        it will raise an error.
  """
```
<!---->

## ✅ Requirements

- Linux-like environment
  - Why: Uses pexpect.spawn().
- Python 3.8+
  - Why: Some dev dependencies require Python 3.8+.

### Tested Platforms

- WSL2 Ubuntu 20.04, Python `3.8.0`.
- Ubuntu 20.04, Python `3.8.0, 3.9.0, 3.10.0, 3.11.0, 3.12.0`, tested in GitHub Actions
  workflow ([build-and-test.yml](./.github/workflows/build-and-test.yml)).

## 🚸 Gotchas and Limitations

- **Security:** This tool is NOT designed to be used with untrusted input. It is
  designed to be used with your own codebase. Even when using your own input, be
  careful that your own code won't be doing anything that might inadvertently
  include untrusted input.
- Be careful to escape `{{` and `}}`,
  or `{%` and `%}` or anything jinja2
  is sensitive to, in the templates. You'll have to escape it properly for
  jinja2, which involves using `{% raw %}` and
  `{% endraw %}` tags.
- Recursion: Snipinator doesn't directly support recursive
  inclusion of generated content. You can generate the contents of one file
  first, and include that generated content into another template. This would
  mean that you have to worry about order of generation.
- Embedded Backticks: If there are backticks in the included snippet, it might
  ruin the backticks you have in your markdown. This is why `backtickify`
  parameter exists in the API, so that Snipinator provides the
  backticks, and it will detect if there are backticks in the snippet and use a
  different number of backticks on the entire snippet. So if the snippet
  contains ` ```My Snippet``` `, Snipinator will use
  ` ````language ```My Snippet``` ```` ` and this is a method that Markdown uses
  to allow embedded backticks inside a code block.
- Formatting: The `{{` `}}` used to
  surround the snippet calls will unfortunately be formatted by a Markdown
  formatter and make the call invalid. Workarounds:
  - **Decommentify**: Put the snippet call inside a HTML comment, then use
    `decommentify` parameter. See
    [./snipinator/examples/LONG-EXAMPLE.md.jinja2](./snipinator/examples/LONG-EXAMPLE.md.jinja2) for
    examples.
  - [prettier](https://prettier.io/) formatter is pretty good at leaving the
    Jinja2 calls alone, especially if you don't have any spaces. This especially
    helps for markdown "reference-style links" that have Jinja2 calls in them
    generating part of the URL, mdformat will URL encode the Jinja2 calls,
    and/or split them on spaces, which is not what we want. prettier will leave
    them alone.
  - For code blocks: If you embed the snippet call in a code block, it will not
    be formatted. However, because of **Embedded Backticks** gotcha, (see
    above), this is not recommended, unless you know for sure that there are no
    embedded backticks.
  - If your formatter supports a comment that disabled formatting, you can
    surround the snippet call with that comment.
- Editing the wrong file: When you have a template and a generated file, it is
  easy to edit the wrong file. To combat this:
  - Snipinator provides a warning at the top of the generated file
    to remind you that it is auto-generated.
  - Snipinator will optionally chmod the file for you to make it
    read-only.
- Newlines: This program assumes LF newlines. I don't know if it will work for
  anything else.
- Combining `backtickify` and `indent`: Doesn't make much sense, but if you do
  it, it will run backtickify first, then indent everything including the
  backticks.

## 🤏 Versioning

We use SemVer for versioning. For the versions available, see the tags on this
repository.

## 🔑 License

This project is licensed under the MIT License - see the
[./LICENSE.md](./LICENSE.md) file for details.

## 🙏 Thanks

Main libraries used in Snipinator are:

- Templating: [Jinja2](https://github.com/pallets/jinja).
- Snippet inclusion: Python's AST library.
- Colorful CLI help: [rich-argparse](https://github.com/hamdanal/rich-argparse).
- ANSI coloring shell output:
  {[pexpect](https://pexpect.readthedocs.io/en/stable/),
  [rich](https://github.com/Textualize/rich)}.

## 🤝 Related Projects

Not complete, and not necessarily up to date. Make a PR
([contributions](#-contributions)) to insert/modify.

| Project                                                           | Stars     | Last Update  | Language   | Platform         | Similarity X Obviousness |
| ----------------------------------------------------------------- | --------- | ------------ | ---------- | ---------------- | ------------------------ |
| [mdx-js/mdx][24]                                                  | 16.8k     | `2024/04/17` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [zakhenry/embedme][25]                                            | 222       | `2023/11/08` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [cmacmackin/markdown-include][26]                                 | 95        | `2023/02/07` | Python     | N/A              | ⭐⭐⭐⭐⭐               |
| [SimonCropp/MarkdownSnippets][27]                                 | 23        | `2024/04/23` | .NET       | N/A              | ⭐⭐⭐⭐⭐               |
| [endocode/snippetextractor][28]                                   | 4         | `2014/08/16` | C++        | N/A              | ⭐⭐⭐⭐⭐               |
| [polywrap/doc-snippets][29]                                       | 3         | `2023/09/26` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [JulianCataldo/remark-embed][30]                                  | 2         | `2022/09/22` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [xrd/oreilly-snippets][31]                                        | 2         | `2015/10/15` | Ruby       | N/A              | ⭐⭐⭐⭐⭐               |
| [DamonOehlman/injectcode][32]                                     | 1         | `2021/08/01` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [electrovir/markdown-code-example-inserter][33]                   | 1         | `2024/02/19` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [andersfischernielsen/Simple-Embedded-Markdown-Code-Snippets][34] | 1         | `2021/02/12` | JS         | N/A              | ⭐⭐⭐⭐⭐               |
| [ildar-shaimordanov/git-markdown-snippet][35]                     | 0         | `2021/09/14` | Perl       | N/A              | ⭐⭐⭐⭐⭐               |
| [teyc/markdown-snippet][36]                                       | 0         | `2024/01/22` | Powershell | N/A              | ⭐⭐⭐⭐⭐               |
| [marc-bouvier-graveyard/baldir_markdown][37]                      | 0         | `2020/06/15` | Python     | N/A              | ⭐⭐⭐⭐⭐               |
| [dineshsonachalam/markdown-autodocs][38]                          | 176       | `2022/09/19` | JS         | GH Action        | ⭐⭐⭐⭐                 |
| [tokusumi/markdown-embed-code][39]                                | 28        | `2022/01/05` | Python     | VSCode Extension | ⭐⭐⭐⭐                 |
| [sammndhr/gridsome-remark-embed-snippet][40]                      | 2         | `2021/06/14` | JS         | [Gridsome][41]   | ⭐⭐⭐⭐                 |
| [NativeScript/markdown-snippet-injector][42]                      | 4         | `2019/01/24` | JS         | N/A              | ⭐⭐⭐⭐                 |
| [fuxingloh/remark-code-import-replace][43]                        | 0         | `2022/12/21` | JS         | Remark?          | ⭐⭐⭐⭐                 |
| [szkiba/mdcode][44]                                               | 15        | `2014/02/12` | Go         | N/A              | ⭐⭐⭐                   |
| [devincornell/pymddoc][45]                                        | 0         | `2023/12/01` | Python     | Python           | ⭐⭐⭐                   |
| [shiftkey/scribble][46] ([docs][47])                              | 40        | `2013/08/08` | .NET       | N/A              | ⭐⭐                     |
| [calebpeterson/jest-transformer-test-md][48]                      | 2         | `2020/08/21` | JS         | Jest Tests       | ⭐⭐                     |
| [tjstankus/commitate][49]                                         | 0         | `2014/05/29` | Ruby       | N/A              | ⭐                       |
| [GitHub Docs: Creating a permanent link to a code snippet][50]    | N/A       | N/A          | N/A        | N/A              | ⭐                       |
| [javierfernandes/markdown-exercises][51]                          | 1         | `2017/05/01` | JS         | N/A              | ⭐                       |
| [gatsby-remark-embed-snippet][52]                                 | N/A (55k) | `2024/01/23` | JS         | [Gatsby][53]     | ⭐                       |
| [ARMmbed/snippet][54]                                             | 6         | `2021/08/05` | Python     | N/A              | ?                        |
| [drewavis/markdowninclude][55]                                    | 1         | `2024/04/06` | JS         | VSCode Extension | ?                        |
| [romnn/embedme][56]                                               | 0         | `2024/04/18` | Go         | N/A              | ?                        |

## 🫡 Contributions

### Development environment: Linux-like

- For running `pre.sh` (Linux-like environment).

  - From [./.github/dependencies.yml](./.github/dependencies.yml), which is used for
    the GH Action to do a fresh install of everything:

    ```yaml
    bash: scripts.
    findutils: scripts.
    grep: tests.
    xxd: tests.
    git: scripts, tests.
    xxhash: scripts (changeguard).
    rsync: out-of-directory test.
    expect: for `unbuffer`, useful to grab and compare ansi color symbols.
    jq: dependency for [yq](https://github.com/kislyuk/yq), which is used to generate
      the README; the README generator needs to use `tomlq` (which is a part of `yq`)
      to query `pyproject.toml`.
    
    ```

  - Requires `pyenv`, or an exact matching version of python as in
    [.python-version](.python-version) (which is currently
    `3.8.0`).
  - act (to run the GH Action locally):
    - Requires nodejs.
    - Requires Go.
    - docker.
  - Generate animation:
    - docker

### Commit Process

1. (Optionally) Fork the `develop` branch.
2. Stage your files: `git add path/to/file.py`.
3. `bash ./scripts/pre.sh`, this will format, lint, and test the code.
4. `git status` check if anything changed (generated
   [./README.md](./README.md) for example), if so, `git add` the
   changes, and go back to the previous step.
5. `git commit -m "..."`.
6. Make a PR to `develop` (or push to develop if you have the rights).

## 🔄🚀 Release Process

These instructions are for maintainers of the project.

1. In the `develop` branch, run `bash ./scripts/pre.sh` to ensure
   everything is in order.
2. In the `develop` branch, bump the version in
   [./pyproject.toml](./pyproject.toml), following semantic versioning
   principles. Also modify the `last_unstable_release` and `last_stable_release`
   in the `[tool.snipinator-project-metadata]` table as appropriate. Run
   `bash ./scripts/pre.sh` to ensure everything is in order.
3. In the `develop` branch, commit these changes with a message like
   `"Prepare release X.Y.Z"`. (See the contributions section
   [above](#commit-process)).
4. Merge the `develop` branch into the `master` branch:
   `git checkout master && git merge develop --no-ff`.
5. `master` branch: Tag the release: Create a git tag for the release with
   `git tag -a vX.Y.Z -m "Version X.Y.Z"`.
6. Publish to PyPI: Publish the release to PyPI with
   `bash ./scripts/deploy-to-pypi.sh`.
7. Push to GitHub: Push the commit and tags to GitHub with
   `git push && git push --tags`.
8. The `--no-ff` option adds a commit to the master branch for the merge, so
   refork the develop branch from the master branch:
   `git checkout develop && git merge master`.
9. Push the develop branch to GitHub: `git push origin develop`.

[1]: ./.github/logo-exported.svg
[2]: https://github.com/realazthat/snipinator
[3]:
  https://img.shields.io/badge/Audience-Developers-0A1E1E?style=plastic&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXVzZXJzIj48cGF0aCBkPSJNMTYgMjF2LTJhNCA0IDAgMCAwLTQtNEg2YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIyIDIxdi0yYTQgNCAwIDAgMC0zLTMuODciLz48cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+
[4]:
  https://img.shields.io/badge/Platform-Linux-0A1E1E?style=plastic&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWxhcHRvcC1taW5pbWFsIj48cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTIiIHg9IjMiIHk9IjQiIHJ4PSIyIiByeT0iMiIvPjxsaW5lIHgxPSIyIiB4Mj0iMjIiIHkxPSIyMCIgeTI9IjIwIi8+PC9zdmc+
[5]:
  https://img.shields.io/github/languages/top/realazthat/snipinator.svg?cacheSeconds=28800&style=plastic&color=0A1E1E
[6]:
  https://img.shields.io/github/license/realazthat/snipinator?style=plastic&color=0A1E1E
[7]: ./LICENSE.md
[8]:
  https://img.shields.io/pypi/v/snipinator?style=plastic&color=0A1E1E
[9]: https://pypi.org/project/snipinator/
[10]:
  https://img.shields.io/pypi/pyversions/snipinator?style=plastic&color=0A1E1E
[11]: https://github.com/realazthat/snipinator/tree/master
[12]:
  https://img.shields.io/github/actions/workflow/status/realazthat/snipinator/build-and-test.yml?branch=master&style=plastic
[13]:
  https://github.com/realazthat/snipinator/actions/workflows/build-and-test.yml
[14]:
  https://img.shields.io/github/commits-since/realazthat/snipinator/v1.4.1/master?style=plastic
[15]:
  https://github.com/realazthat/snipinator/compare/v1.4.1...master
[16]:
  https://img.shields.io/github/last-commit/realazthat/snipinator/master?style=plastic
[17]: https://github.com/realazthat/snipinator/tree/develop
[18]:
  https://img.shields.io/github/actions/workflow/status/realazthat/snipinator/build-and-test.yml?branch=develop&style=plastic
[19]:
  https://img.shields.io/github/commits-since/realazthat/snipinator/v1.4.1/develop?style=plastic
[20]:
  https://github.com/realazthat/snipinator/compare/v1.4.1...develop
[21]:
  https://img.shields.io/github/commits-since/realazthat/snipinator/v1.4.1/develop?style=plastic
[22]:
  https://github.com/realazthat/snipinator/compare/v1.4.1...develop
[23]:
  https://img.shields.io/github/last-commit/realazthat/snipinator/develop?style=plastic
[24]: https://github.com/mdx-js/mdx
[25]: https://github.com/zakhenry/embedme
[26]: https://github.com/cmacmackin/markdown-include
[27]: https://github.com/SimonCropp/MarkdownSnippets
[28]: https://github.com/endocode/snippetextractor
[29]: https://github.com/polywrap/doc-snippets
[30]: https://github.com/JulianCataldo/remark-embed
[31]: https://github.com/xrd/oreilly-snippets
[32]: https://github.com/DamonOehlman/injectcode
[33]: https://github.com/electrovir/markdown-code-example-inserter
[34]:
  https://github.com/andersfischernielsen/Simple-Embedded-Markdown-Code-Snippets
[35]: https://github.com/ildar-shaimordanov/git-markdown-snippet
[36]: https://github.com/teyc/markdown-snippet
[37]: https://github.com/marc-bouvier-graveyard/baldir_markdown
[38]: https://github.com/dineshsonachalam/markdown-autodocs
[39]: https://github.com/tokusumi/markdown-embed-code
[40]: https://github.com/sammndhr/gridsome-remark-embed-snippet
[41]: https://gridsome.org/
[42]: https://github.com/NativeScript/markdown-snippet-injector
[43]: https://github.com/fuxingloh/remark-code-import-replace
[44]:
  https://github.com/szkiba/mdcode
  "Extracts code blocks from README and produces tests; a similar approach, but quite different"
[45]: https://github.com/devincornell/pymddoc
[46]: https://github.com/shiftkey/scribble
[47]:
  https://github.com/shiftkey/scribble/blob/master/docs/features/code-snippets.md
[48]: https://github.com/calebpeterson/jest-transformer-test-md
[49]: https://github.com/tjstankus/commitate
[50]:
  https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-a-permanent-link-to-a-code-snippet
[51]: https://github.com/javierfernandes/markdown-exercises
[52]:
  https://github.com/gatsbyjs/gatsby/tree/master/packages/gatsby-remark-embed-snippet
[53]: https://github.com/gatsbyjs/gatsby
[54]: https://github.com/ARMmbed/snippet
[55]: https://github.com/drewavis/markdowninclude
[56]: https://github.com/romnn/embedme
