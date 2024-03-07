# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
#
# The Snipinator project requires contributions made to this file be licensed
# under the MIT license or a compatible open source license. See LICENSE.md for
# the license text.

import unittest
from pathlib import Path

from .snipinate import _Context, path


class SnipinateTest(unittest.TestCase):

  def _MakeContext(self):
    return _Context(cwd=Path.cwd(), template_file_name='-', written_files=set())

  def test_path(self):
    self.assertEqual('snipinator/snipinate.py',
                     path('snipinator/snipinate.py', _ctx=self._MakeContext()))

  def test_path_fails(self):
    self.assertRaises(FileNotFoundError,
                      path,
                      'snipinator/does_not_exist.py',
                      _ctx=self._MakeContext())


if __name__ == '__main__':
  unittest.main()
