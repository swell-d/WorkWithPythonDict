import unittest
from unittest import TestSuite

from CheckTypes import CheckTypesTests
from Deepl import DeeplTests
from LoadDictFromFile import LoadDictFromFileTests
from SaveDictToFile import SaveDictToFileTests
from Sw import SwTests
from TextCorrections import TextCorrectionsTests


def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for test_class in (
            CheckTypesTests,
            DeeplTests,
            LoadDictFromFileTests,
            SaveDictToFileTests,
            SwTests,
            TextCorrectionsTests
    ):
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


unittest.main(verbosity=2)
