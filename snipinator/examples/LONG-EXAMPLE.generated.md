<!--

WARNING: This file is auto-generated. Do not edit directly.
SOURCE: `snipinator/examples/LONG-EXAMPLE.md.jinja2`.

-->
# A README

Here is a code snippet (global class):

````py
class MyClass:
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
````

______________________________________________________________________

Here is a code snippet (class member method):

````py
  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)
````

\--

Same thing but just the signature:

````py
  def MyClassMethod(self):
    """This is a method of MyClass"""
````

______________________________________________________________________

Here is a code snippet (global method):

````py
async def GlobalMethod():
  """This is a global method"""
  print('Hello')
````

______________________________________________________________________

Here is a terminal snippet:

````shell
$ls -la snipinator/examples/code.py
-rwxrwxrwx 1 realz realz 497 Feb 29 00:27 snipinator/examples/code.py

````

______________________________________________________________________

Here is a terminal snippet with terminal colors (img tag with svg data):

<!--
--><img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/Pgo8c3ZnIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgY2xhc3M9InJpY2gtdGVybWluYWwiIHZpZXdCb3g9IjAgMCA5OTQgOTguOCI+CjwhLS0gR2VuZXJhdGVkIHdpdGggUmljaCB0ZXh0dWFsaXplLmlvIC0tPgo8c3R5bGU+CkBmb250LWZhY2Ugewpmb250LWZhbWlseTogJnF1b3Q7RmlyYSBDb2RlJnF1b3Q7OwpzcmM6IGxvY2FsKCZxdW90O0ZpcmFDb2RlLVJlZ3VsYXImcXVvdDspLAp1cmwoJnF1b3Q7aHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvZmlyYWNvZGUvNi4yLjAvd29mZjIvRmlyYUNvZGUtUmVndWxhci53b2ZmMiZxdW90OykgZm9ybWF0KCZxdW90O3dvZmYyJnF1b3Q7KSwKdXJsKCZxdW90O2h0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2ZpcmFjb2RlLzYuMi4wL3dvZmYvRmlyYUNvZGUtUmVndWxhci53b2ZmJnF1b3Q7KSBmb3JtYXQoJnF1b3Q7d29mZiZxdW90Oyk7CmZvbnQtc3R5bGU6IG5vcm1hbDsKZm9udC13ZWlnaHQ6IDQwMDsKfQpAZm9udC1mYWNlIHsKZm9udC1mYW1pbHk6ICZxdW90O0ZpcmEgQ29kZSZxdW90OzsKc3JjOiBsb2NhbCgmcXVvdDtGaXJhQ29kZS1Cb2xkJnF1b3Q7KSwKdXJsKCZxdW90O2h0dHBzOi8vY2RuanMuY2xvdWRmbGFyZS5jb20vYWpheC9saWJzL2ZpcmFjb2RlLzYuMi4wL3dvZmYyL0ZpcmFDb2RlLUJvbGQud29mZjImcXVvdDspIGZvcm1hdCgmcXVvdDt3b2ZmMiZxdW90OyksCnVybCgmcXVvdDtodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9maXJhY29kZS82LjIuMC93b2ZmL0ZpcmFDb2RlLUJvbGQud29mZiZxdW90OykgZm9ybWF0KCZxdW90O3dvZmYmcXVvdDspOwpmb250LXN0eWxlOiBib2xkOwpmb250LXdlaWdodDogNzAwOwp9Ci50ZXJtaW5hbC0yNTM3NzY0MjAwLW1hdHJpeCB7CmZvbnQtZmFtaWx5OiBGaXJhIENvZGUsIG1vbm9zcGFjZTsKZm9udC1zaXplOiAyMHB4OwpsaW5lLWhlaWdodDogMjQuNHB4Owpmb250LXZhcmlhbnQtZWFzdC1hc2lhbjogZnVsbC13aWR0aDsKfQoudGVybWluYWwtMjUzNzc2NDIwMC10aXRsZSB7CmZvbnQtc2l6ZTogMThweDsKZm9udC13ZWlnaHQ6IGJvbGQ7CmZvbnQtZmFtaWx5OiBhcmlhbDsKfQoudGVybWluYWwtMjUzNzc2NDIwMC1yMSB7IGZpbGw6ICNkOWQ5ZDkgfQo8L3N0eWxlPgo8ZGVmcz4KPGNsaXBQYXRoIGlkPSJ0ZXJtaW5hbC0yNTM3NzY0MjAwLWNsaXAtdGVybWluYWwiPgo8cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iOTc1LjAiIGhlaWdodD0iNDcuOCIvPgo8L2NsaXBQYXRoPgo8Y2xpcFBhdGggaWQ9InRlcm1pbmFsLTI1Mzc3NjQyMDAtbGluZS0wIj4KPHJlY3QgeD0iMCIgeT0iMS41IiB3aWR0aD0iOTc2IiBoZWlnaHQ9IjI0LjY1Ii8+CjwvY2xpcFBhdGg+CjwvZGVmcz4KPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoOSwgMCkiPgo8ZyBjbGFzcz0idGVybWluYWwtMjUzNzc2NDIwMC1tYXRyaXgiPgo8dGV4dCBjbGFzcz0idGVybWluYWwtMjUzNzc2NDIwMC1yMSIgeD0iMCIgeT0iMjAiIHRleHRMZW5ndGg9IjQyNyIgY2xpcC1wYXRoPSJ1cmwoI3Rlcm1pbmFsLTI1Mzc3NjQyMDAtbGluZS0wKSI+JGxzwqAtbGHCoHNuaXBpbmF0b3IvZXhhbXBsZXMvY29kZS5weTwvdGV4dD4KPHRleHQgY2xhc3M9InRlcm1pbmFsLTI1Mzc3NjQyMDAtcjEiIHg9Ijk3NiIgeT0iMjAiIHRleHRMZW5ndGg9IjEyLjIiIGNsaXAtcGF0aD0idXJsKCN0ZXJtaW5hbC0yNTM3NzY0MjAwLWxpbmUtMCkiPgo8L3RleHQ+Cjx0ZXh0IGNsYXNzPSJ0ZXJtaW5hbC0yNTM3NzY0MjAwLXIxIiB4PSIwIiB5PSI0NC40IiB0ZXh0TGVuZ3RoPSI4NDEuOCIgY2xpcC1wYXRoPSJ1cmwoI3Rlcm1pbmFsLTI1Mzc3NjQyMDAtbGluZS0xKSI+LXJ3eHJ3eHJ3eMKgMcKgcmVhbHrCoHJlYWx6wqA0OTfCoEZlYsKgMjnCoDAwOjI3wqBzbmlwaW5hdG9yL2V4YW1wbGVzL2NvZGUucHk8L3RleHQ+Cjx0ZXh0IGNsYXNzPSJ0ZXJtaW5hbC0yNTM3NzY0MjAwLXIxIiB4PSI5NzYiIHk9IjQ0LjQiIHRleHRMZW5ndGg9IjEyLjIiIGNsaXAtcGF0aD0idXJsKCN0ZXJtaW5hbC0yNTM3NzY0MjAwLWxpbmUtMSkiPgo8L3RleHQ+CjwvZz4KPC9nPgo8L3N2Zz4="/><!--
-->

______________________________________________________________________

Here is a terminal snippet with terminal colors (raw svg):

<!--
--><?xml version="1.0" ?>
<svg xmlns="http://www.w3.org/2000/svg" class="rich-terminal" viewBox="0 0 994 98.8">
<!-- Generated with Rich textualize.io -->
<style>
@font-face {
font-family: &quot;Fira Code&quot;;
src: local(&quot;FiraCode-Regular&quot;),
url(&quot;https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2&quot;) format(&quot;woff2&quot;),
url(&quot;https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff&quot;) format(&quot;woff&quot;);
font-style: normal;
font-weight: 400;
}
@font-face {
font-family: &quot;Fira Code&quot;;
src: local(&quot;FiraCode-Bold&quot;),
url(&quot;https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2&quot;) format(&quot;woff2&quot;),
url(&quot;https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff&quot;) format(&quot;woff&quot;);
font-style: bold;
font-weight: 700;
}
.terminal-2537764200-matrix {
font-family: Fira Code, monospace;
font-size: 20px;
line-height: 24.4px;
font-variant-east-asian: full-width;
}
.terminal-2537764200-title {
font-size: 18px;
font-weight: bold;
font-family: arial;
}
.terminal-2537764200-r1 { fill: #d9d9d9 }
</style>
<defs>
<clipPath id="terminal-2537764200-clip-terminal">
<rect x="0" y="0" width="975.0" height="47.8"/>
</clipPath>
<clipPath id="terminal-2537764200-line-0">
<rect x="0" y="1.5" width="976" height="24.65"/>
</clipPath>
</defs>
<g transform="translate(9, 0)">
<g class="terminal-2537764200-matrix">
<text class="terminal-2537764200-r1" x="0" y="20" textLength="427" clip-path="url(#terminal-2537764200-line-0)">$ls -la snipinator/examples/code.py</text>
<text class="terminal-2537764200-r1" x="976" y="20" textLength="12.2" clip-path="url(#terminal-2537764200-line-0)">
</text>
<text class="terminal-2537764200-r1" x="0" y="44.4" textLength="841.8" clip-path="url(#terminal-2537764200-line-1)">-rwxrwxrwx 1 realz realz 497 Feb 29 00:27 snipinator/examples/code.py</text>
<text class="terminal-2537764200-r1" x="976" y="44.4" textLength="12.2" clip-path="url(#terminal-2537764200-line-1)">
</text>
</g>
</g>
</svg><!--
-->

______________________________________________________________________
