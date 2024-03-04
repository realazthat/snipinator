# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.

import unittest
from pathlib import Path

from .snipinate import path


class SnipinateTest(unittest.TestCase):

  def test_path(self):
    self.assertEqual('snipinator/snipinate.py',
                     path('snipinator/snipinate.py', cwd=Path.cwd()))

  def test_path_fails(self):
    self.assertRaises(FileNotFoundError,
                      path,
                      'snipinator/does_not_exist.py',
                      cwd=Path.cwd())


if __name__ == '__main__':
  unittest.main()
