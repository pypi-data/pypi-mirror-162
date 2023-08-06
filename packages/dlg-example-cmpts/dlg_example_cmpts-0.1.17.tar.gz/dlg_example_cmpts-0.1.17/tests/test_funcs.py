import pytest, unittest
import os
import pickle
import urllib
import http

from glob import glob
from dlg import droputils

from dlg_example_funcs import simple
from dlg.apps.pyfunc import PyFuncApp
from dlg.drop import FileDROP, InMemoryDROP, NullDROP
from dlg.ddap_protocol import DROPStates
import logging
import json

logger = logging.Logger(__name__)

given = pytest.mark.parametrize


class TestMyFuncs(unittest.TestCase):
    def test_output(self):
        result = simple.output("World", kw="")
        self.assertEqual(result, "Hello World and ")
