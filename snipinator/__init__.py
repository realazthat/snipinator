# Notes
#
# * https://versioningit.readthedocs.io/en/stable/runtime-version.html#getting-package-version-at-runtime
#
#
import sys

if sys.version_info >= (3, 8):
  from importlib.metadata import PackageNotFoundError
  from importlib.metadata import version as importlib_version
else:
  from importlib_metadata import PackageNotFoundError
  from importlib_metadata import version as importlib_version

try:
  _build_version = importlib_version('snipinator')
except PackageNotFoundError:
  _build_version = '0.0.0'
