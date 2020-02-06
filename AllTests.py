import unittest

from CheckTypes import CheckTypesTests
from Deepl import DeeplTests
from FindDigits import FindDigitsTests
from LoadDictFromFile import LoadDictFromFileTests
from SaveDictToFile import SaveDictToFileTests
from Sw import SwTests


def tmp():
    CheckTypesTests()
    DeeplTests()
    FindDigitsTests()
    LoadDictFromFileTests()
    SaveDictToFileTests()
    SwTests()


if __name__ == '__main__':
    unittest.main(verbosity=0)
