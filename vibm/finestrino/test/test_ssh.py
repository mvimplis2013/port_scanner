import subprocess
import unittest

from finestrino.contrib.ssh import RemoteContext

class TestMockedRemoteContext(unittest.TestCase):
    def test_subprocess_delegation(self):
        pass