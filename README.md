<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `README.md.jinja2`.

-->
# Snipinator

Make your `README.md` into a Jinja2 template for including snippets from your
python codebase. Uses Jinja2, and Python's AST library.

## What

What it does: Lets you make a `EXAMPLE.md` template and include snippets from
your (working and tested) python codebase.

Turn this (`snipinator/examples/EXAMPLE.md.jinja2`):

````md
# A README

Here is a code snippet:

`{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py') }}`

````

Into this (`snipinator/examples/EXAMPLE.generated.jinja2`):

``````md
<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

````py
class MyClass:

  def __init__(self, name):
    self.name = name

  def __str__(self):
    return f'MyClass({self.name})'

  def __repr__(self):
    return f'MyClass({self.name})'
````

``````

## Getting Started

### Install

```bash
# Install from git (https://github.com/realazthat/snipinator)
pip install git+https://github.com/realazthat/snipinator.git
```

### Use

`snipinator/examples/EXAMPLE.md.jinja2`:

````md
# A README

Here is a code snippet:

`{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py') }}`

````

````bash
$python -m snipinator.cli --help
usage: python -m snipinator.cli [-h] -t TEMPLATE [--cwd CWD] [-a ARGS]
                                [--templates-searchpath TEMPLATES_SEARCHPATH]
                                [-o OUTPUT]
                                [--warning-message WARNING_MESSAGE]
                                [--chmod CHMOD]

CLI: Python code snipinator for markdown files, e.g READMEs, from actual
(testable) code.

options:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        Path to the template file. Use "-" for stdin.
  --cwd CWD             Directory to use as the base for snippet paths in the
                        template. Defaults to the current working directory.
  -a ARGS, --args ARGS  JSON string with template arguments. Defaults to {}.
  --templates-searchpath TEMPLATES_SEARCHPATH
                        Path to the directory with templates for include
                        directives etc. Defaults to None.
  -o OUTPUT, --output OUTPUT
                        Path to the output file. Use "-" for stdout. Defaults
                        to "-".
  --warning-message WARNING_MESSAGE
                        Warning message to include in the output file. To
                        prevent accidentally editing generated file.Defaults
                        to the default warning message.
  --chmod CHMOD         Change the mode (permissions) of the output file, an
                        octant (see chmod help for more info) e.g 444 or 555.
                        To prevent accidentally editing generated file.
                        Defaults to None.

````

``````bash
$python -m snipinator.cli -t snipinator/examples/EXAMPLE.md.jinja2
<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

````py
class MyClass:

  def __init__(self, name):
    self.name = name

  def __str__(self):
    return f'MyClass({self.name})'

  def __repr__(self):
    return f'MyClass({self.name})'
````

``````

## Available Functions in Jinja2

````py
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
````
````py
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
````
````py
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

````
````py
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

````
````py
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

````

## Gotchas

- **Security:** This tool is not designed to be used with untrusted input. It is
  designed to be used with your own codebase. Even so, be careful that your own
  code won't be doing weird things.
- Be careful to escape `{{` and `}}`,
  or `{%` and `%}` or anything jinja2
  is sensitive to, in the templates. You'll have to escape it properly.
- Recursion: Snipinator doesn't directly support recursive inclusion of
  generated content. You can generate the contents of one file first, and
  include that generated content into another template. This would mean that you
  have to worry about order of generation.
- Embedded Backticks: If there are backticks in the included snippet, it might
  ruin the backticks you have in your markdown. This is why `backtickify`
  parameter exists in the API, so that Snipinator provides the backticks, and it
  will detect if there are backticks in the snippet and use a different number
  of backticks on the entire snippet. So if the snippet contains
  ```` ```My Snippet``` ````, Snipinator will use
  ````` ````language ```My Snippet``` ```` ````` and this is a method that
  Markdown uses to allow embedded backticks inside a code block.
- Formatting: The `{{` `}}` used to
  surround the snippet calls will unfortunately be formatted by a Markdown
  formatter and make the call invalid. Workarounds:
  - For code blocks: If you embed the snippet call in a code block, it will not
    be formatted. However, because of **Embedded Backticks** gotcha, (see
    above), this is not recommended, unless you know for sure that there are no
    embedded backticks.
  - If your formatter supports a comment that disabled formatting, you can
    surround the snippet call with that comment.
- Editing the wrong file: When you have a template and a generated file, it is
  easy to edit the wrong file. To combat this:
  - Snipinator provides a warning at the top of the generated file to remind you
    that it is auto-generated.
  - Snipinator will optionally chmod the file for you to make it read-only.
- Newlines: This program assumes LF newlines. I don't know if it will work for
  anything else.
- Combining `backtickify` and `indent`: Doesn't make much sense, but if you do
  it, it will run backtickify first, then indent everything including the
  backticks.

## Examples

- Snipinator's own `README` at
  [`./README.md.jinja2`](./README.md.jinja2).
  - Generated: [`./README.md`](./README.md).
- [`snipinator/examples/EXAMPLE.md.jinja2`](./snipinator/examples/EXAMPLE.md.jinja2).
  - Generated:
    [`snipinator/examples/EXAMPLE.generated.md`](./snipinator/examples/EXAMPLE.generated.md).
