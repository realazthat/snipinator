<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `README.md.jinja2`.

-->
# Snipinator

![Top language][9] ![GitHub License][3] [![PyPI - Version][4]][5]
[![Python Version][8]][5]

|        | Status                    |                                      |
| ------ | ------------------------- | ------------------------------------ |
| Master | [![Build and Test][1]][2] | ![since tagged][6] ![last commit][7] |

CLI to embed snippets from your python codebase into your `README.md`. Uses
Jinja2, and Python's AST library.

## What

What it does: Lets you make a `EXAMPLE.md` template and include snippets from
your (working and tested) python codebase.

Turn this (`snipinator/examples/EXAMPLE.md.jinja2`):

````md
# A README

Here is a code snippet:

`{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py') }}`

````

Into this (`snipinator/examples/EXAMPLE.generated.md`):

``````md
<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

````py
class MyClass:
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
````

``````

## Getting Started

### Install

**Requirements:**

- Linux-like environment
  - Why: Uses chmod, rm, and pexpect.spawn().
- Python 3.10+
  - Why: uses PEP 604, pipe type hints for Union.

```bash
# Install from pypi (https://pypi.org/project/snipinator/)
pip install snipinator

# Install from git (https://github.com/realazthat/snipinator)
pip install git+https://github.com/realazthat/snipinator.git@v1.0.4
```

**Tested on:**

- WSL2 Ubuntu 20.04, Python 3.10.1
- Ubuntu 20.04, Python 3.10.1

### Use

`snipinator/examples/EXAMPLE.md.jinja2`:

````md
# A README

Here is a code snippet:

`{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass', backtickify='py') }}`

````

<!----><img src="README.help.generated.svg"/><!---->

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
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
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
````
````py
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
````
````py
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

````
````py
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

````
````py
def shell(args: str,
          *,
          escape: bool = False,
          indent: str | int | None = None,
          backtickify: bool | str = False,
          decomentify: bool = False,
          rich: Literal['svg'] | Literal['img+b64+svg'] | Literal['raw']
          | str = 'raw',
          cwd: Path,
          template_file_name: str) -> str | markupsafe.Markup:
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
      rich (Literal['svg']|Literal['img+b64+svg']|Literal['raw']|str, optional):
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
      cwd (Path): This is used by the system and is not available as an
        argument. You can change this on the command line.
      template_file_name (Path): This is used by the system and is not available
        as an argument.

  Returns:
      str | markupsafe.Markup: Returns the output of the command.
  """
````

Also see Jinja2 v3
[Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/).

## Gotchas

- **Security:** This tool is NOT designed to be used with untrusted input. It is
  designed to be used with your own codebase. Even when using your own input, be
  careful that your own code won't be doing anything that might inadvertently
  include untrusted input.
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
  - Generation script:
    [`./scripts/generate-readme.sh`](./scripts/generate-readme.sh).
- [`snipinator/examples/EXAMPLE.md.jinja2`](./snipinator/examples/EXAMPLE.md.jinja2).
  - Generated:
    [`snipinator/examples/EXAMPLE.generated.md`](./snipinator/examples/EXAMPLE.generated.md).
  - Generation script:
    [`./snipinator/examples/example.sh`](./snipinator/examples/example.sh).

## Contributions

1. Fork the `master` branch.
2. Stage your files: `git add path/to/file.py`.
3. `bash scripts/pre.sh`, this will format, lint, and test the code.
4. `git status` check if anything changed (generated README for example), if so,
   `git add` the changes, and go back to the previous step.
5. `git commit -m "..."`.
6. Make a PR to `master`.

## Release Process

1. Bump the version in setup.py, following semantic versioning principles.
2. Change any reference to the old version (or tag) in the README.md to the new
   version.
3. Commit changes: Commit these changes with a message like "Prepare release
   X.Y.Z". (See the contributions section [above](#contributions)).
4. Tag the release: Create a git tag for the release with
   `git tag -a vX.Y.Z -m "Version X.Y.Z"`.
5. Push to GitHub: Push the commit and tags to GitHub with `git push` and
   `git push --tags`.
6. Publish to PyPI: Publish the release to PyPI with
   `bash scripts/deploy-to-pypi.sh`.

[1]: https://github.com/realazthat/snipinator/actions/workflows/build-and-test.yml/badge.svg?branch=master
[2]: https://github.com/realazthat/snipinator/actions/workflows/build-and-test.yml
[3]: https://img.shields.io/github/license/realazthat/snipinator
[4]: https://img.shields.io/pypi/v/snipinator
[5]: https://pypi.org/project/snipinator/
[6]: https://img.shields.io/github/commits-since/realazthat/snipinator/v1.0.4/master
[7]: https://img.shields.io/github/last-commit/realazthat/snipinator/master
[8]: https://img.shields.io/pypi/pyversions/snipinator
[9]: https://img.shields.io/github/languages/top/realazthat/snipinator.svg?&cacheSeconds=28800
