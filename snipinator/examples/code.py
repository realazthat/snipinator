# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.


class MyClass:
  """This is a global class"""

  def __init__(self, name):
    self.name = name

  def MyClassMethod(self):
    """This is a method of MyClass"""
    print(self.name)


async def GlobalMethod():
  """This is a global method"""
  print('Hello')


async def MethodForDelimiterTest():
  """This is a method in a delimiter"""
  print('This is a method in a delimiter')
  # DELIM_TEST_START
  i = 5
  print(i)
  # DELIM_TEST_END
