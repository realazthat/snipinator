# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.

from unittest import TestCase

from .code import MyClass


class TestCode(TestCase):

  def test_MyClass(self):
    my_obj = MyClass('name')
    self.assertEqual(my_obj.name, 'name')


if __name__ == '__main__':
  from unittest import main
  main()
