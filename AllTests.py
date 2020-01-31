import unittest

from CheckTypes import CheckTypesTests
from Deepl import DeeplTests
from LoadDictFromFile import LoadDictFromFileTests
from SaveDictToFile import SaveDictToFileTests
from Sw import SwTests
from TextCorrections import TextCorrectionsTests


def tmp():
    CheckTypesTests()
    DeeplTests()
    LoadDictFromFileTests()
    SaveDictToFileTests()
    SwTests()
    TextCorrectionsTests()


if __name__ == '__main__':
    unittest.main(verbosity=0)
