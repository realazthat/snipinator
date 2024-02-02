# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.


class MyClass:

  def __init__(self, name):
    self.name = name

  def __str__(self):
    return f'MyClass({self.name})'

  def __repr__(self):
    return f'MyClass({self.name})'


async def Method():
  """This is a method"""
  print('Hello')
