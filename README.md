<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `README.md.jinja2`.

-->
# Snipinator

## What

What it does: Lets you make a `EXAMPLE.md` template and include snippets from
your (working and tested) python codebase.

Turn this (`snipinator/examples/EXAMPLE.md.jinja2`):

```md
# A README

Here is a code snippet:

{{ pysnippet(path='snipinator/examples/code.py', symbol='MyClass',
backtickify='py') }}

```

Into this (`snipinator/examples/EXAMPLE.generated.md`):

````md
<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `snipinator/examples/EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet:

```py
class MyClass:

  def __init__(self, name):
    self.name = name

  def __str__(self):
    return f'MyClass({self.name})'

  def __repr__(self):
    return f'MyClass({self.name})'
```

````

## Getting Started

### Install

```bash
# Install from git (https://github.com/realazthat/snipinator)
pip install git+https://github.com/realazthat/snipinator.git
```

### Use

## Jinja2 Functions

## How
