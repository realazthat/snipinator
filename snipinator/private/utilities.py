# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.

from pathlib import Path
from typing import Union, overload

from typing_extensions import Literal


@overload
def GetPath(path: None) -> None:
  ...


@overload
def GetPath(path: Union[Path, str]) -> Path:
  ...


def GetPath(path: Union[Path, str, None]) -> Union[Path, None]:
  if path is None:
    return None
  return Path(path).expanduser()


@overload
def GetIOPath(path: None) -> None:
  ...


@overload
def GetIOPath(path: Union[Path, str]) -> Union[Path, Literal['-']]:
  ...


def GetIOPath(path: Union[Path, str, None]) -> Union[Path, Literal['-'], None]:
  if path == '-':
    return '-'
  return GetPath(path)
