from __future__ import print_function 

from target_test import FileSystemTargetTestMixin

import unittest
class LocalTargetTest(unittest.TestCase, FileSystemTargetTestMixin):
    PATH_PREFIX = '/tmp/test.txt'

