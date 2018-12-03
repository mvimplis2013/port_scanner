from __future__ import print_function

import unittest

import finestrino 

class TestException(Exception):
    pass

class TargetTest(unittest.TestCase):
    def test_cannot_instantiate(self):
        def instantiate_target():
            finestrino.target.Target()


        self.assertRaises(TypeError, instantiate_target)
    
    def test_abstract_subclass(self):
        class ExistsLessTarget(finestrino.target.Target):
            pass

        def instantiate_target():
            ExistsLessTarget()

        self.asserRaises(TypeError, instantiate_target)

    def test_instantiate_subclass(self):
        class GoodTarget(finestrino.target.Target):
            def exists(self):
                return True

            def open(self, mode):
                return None 

        GoodTarget()
