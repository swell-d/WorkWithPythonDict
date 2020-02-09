import re
import unittest


def find_int(text):
    findall = re.findall(re.compile("-?\\d+"), str(text))
    result = []
    for each in findall: result.append(int(each))
    return result or ['']


def find_floats(text, point='.,'):
    SS = f'[^0-9{point}-]'
    float_compile = re.compile(f"{SS}(0){SS}|{SS}(-?0[{point}]\\d+){SS}|{SS}(-?[1-9]\\d*([{point}]\\d+)?){SS}")
    findall = re.findall(float_compile, f" {str(text)} ")
    result = []
    for each in findall: result.append(float((each[2] or each[1] or each[0]).replace(',', '.')))
    return result or ['']


class FindDigitsTests(unittest.TestCase):
    def test_int(self):
        self.assertEqual([''], find_int(''))
        self.assertEqual([''], find_int(' '))
        self.assertEqual([''], find_int('abc'))
        self.assertEqual([0], find_int(0))

        self.assertEqual([0], find_int('0'))
        self.assertEqual([0], find_int('a0b'))
        self.assertEqual([0], find_int('<b>0</b>'))
        self.assertEqual([0], find_int('a 0 b'))

        self.assertEqual([1], find_int('1'))
        self.assertEqual([1], find_int('a1b'))
        self.assertEqual([1], find_int('<b>1</b>'))
        self.assertEqual([1], find_int('a 1 b'))

        self.assertEqual([-1], find_int('-1'))
        self.assertEqual([-1], find_int('a-1b'))
        self.assertEqual([-1], find_int('<b>-1</b>'))
        self.assertEqual([-1], find_int('a -1 b'))

        self.assertEqual([0, 1], find_int('0.1'))
        self.assertEqual([0, 1], find_int('a0.1b'))
        self.assertEqual([0, 1], find_int('<b>0.1</b>'))
        self.assertEqual([0, 1], find_int('a 0.1 b'))

        self.assertEqual([0, 1], find_int('-0.1'))
        self.assertEqual([0, 1], find_int('a-0.1b'))
        self.assertEqual([0, 1], find_int('<b>-0.1</b>'))
        self.assertEqual([0, 1], find_int('a -0.1 b'))

        self.assertEqual([1, 23, 3, 45, 234, 567], find_int('1 23.3.45 234.567'))

        self.assertEqual([1, 23, 3, 45, 234, 567, 123], find_int('1ab23.3,45cd234,567ef123'))

        self.assertEqual([234, 567, 123], find_int('<b>234.567</b>123'))

        self.assertEqual([1, -2], find_int('1-2'))

    def test_float(self):
        self.assertEqual([''], find_floats(''))
        self.assertEqual([''], find_floats(' '))
        self.assertEqual([''], find_floats('abc'))
        self.assertEqual([0], find_floats(0))

        self.assertEqual([0], find_floats('0'))
        self.assertEqual([0], find_floats('a0b'))
        self.assertEqual([0], find_floats('<b>0</b>'))
        self.assertEqual([0], find_floats('a 0 b'))

        self.assertEqual([1], find_floats('1'))
        self.assertEqual([1], find_floats('a1b'))
        self.assertEqual([1], find_floats('<b>1</b>'))
        self.assertEqual([1], find_floats('a 1 b'))

        self.assertEqual([-1], find_floats('-1'))
        self.assertEqual([-1], find_floats('a-1b'))
        self.assertEqual([-1], find_floats('<b>-1</b>'))
        self.assertEqual([-1], find_floats('a -1 b'))

        self.assertEqual([0.1], find_floats('0.1'))
        self.assertEqual([0.1], find_floats('a0.1b'))
        self.assertEqual([0.1], find_floats('<b>0.1</b>'))
        self.assertEqual([0.1], find_floats('a 0.1 b'))

        self.assertEqual([-0.1], find_floats('-0.1'))
        self.assertEqual([-0.1], find_floats('a-0.1b'))
        self.assertEqual([-0.1], find_floats('<b>-0.1</b>'))
        self.assertEqual([-0.1], find_floats('a -0.1 b'))

        self.assertEqual([1, 234.567], find_floats('1 23.3.45 234.567'))

        self.assertEqual([1, 234.567, 123], find_floats('1ab23.3,45cd234,567ef123'))

        self.assertEqual([234.567, 234.567], find_floats('<b>234.567</b>234,567'))

        self.assertEqual([''], find_floats('1-2'))


if __name__ == '__main__':
    unittest.main()
