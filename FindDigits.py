import re
import unittest


class FindDigits:
    POINT = '.,'
    __int_compile = re.compile("-?\\d+")
    __ss = f'[^0-9{POINT}-]'
    __float_compile = re.compile(
        f"{__ss}(0){__ss}|{__ss}(-?0[{POINT}]\\d+){__ss}|{__ss}(-?[1-9]\\d*([{POINT}]\\d+)?){__ss}")

    @classmethod
    def find_int(cls, text):
        findall = re.findall(cls.__int_compile, str(text))
        result = []
        for each in findall: result.append(int(each))
        return result

    @classmethod
    def find_floats(cls, text):
        findall = re.findall(cls.__float_compile, f" {str(text)} ")
        result = []
        for each in findall: result.append(float((each[2] or each[1] or each[0]).replace(',', '.')))
        return result


class FindDigitsTests(unittest.TestCase):
    def test_int(self):
        obj = FindDigits()
        self.assertEqual([], obj.find_int(''))
        self.assertEqual([], obj.find_int(' '))
        self.assertEqual([], obj.find_int('abc'))
        self.assertEqual([0], obj.find_int(0))

        self.assertEqual([0], obj.find_int('0'))
        self.assertEqual([0], obj.find_int('a0b'))
        self.assertEqual([0], obj.find_int('<b>0</b>'))
        self.assertEqual([0], obj.find_int('a 0 b'))

        self.assertEqual([1], obj.find_int('1'))
        self.assertEqual([1], obj.find_int('a1b'))
        self.assertEqual([1], obj.find_int('<b>1</b>'))
        self.assertEqual([1], obj.find_int('a 1 b'))

        self.assertEqual([-1], obj.find_int('-1'))
        self.assertEqual([-1], obj.find_int('a-1b'))
        self.assertEqual([-1], obj.find_int('<b>-1</b>'))
        self.assertEqual([-1], obj.find_int('a -1 b'))

        self.assertEqual([0, 1], obj.find_int('0.1'))
        self.assertEqual([0, 1], obj.find_int('a0.1b'))
        self.assertEqual([0, 1], obj.find_int('<b>0.1</b>'))
        self.assertEqual([0, 1], obj.find_int('a 0.1 b'))

        self.assertEqual([0, 1], obj.find_int('-0.1'))
        self.assertEqual([0, 1], obj.find_int('a-0.1b'))
        self.assertEqual([0, 1], obj.find_int('<b>-0.1</b>'))
        self.assertEqual([0, 1], obj.find_int('a -0.1 b'))

        self.assertEqual([1, 23, 3, 45, 234, 567], obj.find_int('1 23.3.45 234.567'))

        self.assertEqual([1, 23, 3, 45, 234, 567, 123], obj.find_int('1ab23.3,45cd234,567ef123'))

        self.assertEqual([234, 567, 123], obj.find_int('<b>234.567</b>123'))

        self.assertEqual([1, -2], obj.find_int('1-2'))

    def test_float(self):
        obj = FindDigits()
        self.assertEqual([], obj.find_floats(''))
        self.assertEqual([], obj.find_floats(' '))
        self.assertEqual([], obj.find_floats('abc'))
        self.assertEqual([0], obj.find_floats(0))

        self.assertEqual([0], obj.find_floats('0'))
        self.assertEqual([0], obj.find_floats('a0b'))
        self.assertEqual([0], obj.find_floats('<b>0</b>'))
        self.assertEqual([0], obj.find_floats('a 0 b'))

        self.assertEqual([1], obj.find_floats('1'))
        self.assertEqual([1], obj.find_floats('a1b'))
        self.assertEqual([1], obj.find_floats('<b>1</b>'))
        self.assertEqual([1], obj.find_floats('a 1 b'))

        self.assertEqual([-1], obj.find_floats('-1'))
        self.assertEqual([-1], obj.find_floats('a-1b'))
        self.assertEqual([-1], obj.find_floats('<b>-1</b>'))
        self.assertEqual([-1], obj.find_floats('a -1 b'))

        self.assertEqual([0.1], obj.find_floats('0.1'))
        self.assertEqual([0.1], obj.find_floats('a0.1b'))
        self.assertEqual([0.1], obj.find_floats('<b>0.1</b>'))
        self.assertEqual([0.1], obj.find_floats('a 0.1 b'))

        self.assertEqual([-0.1], obj.find_floats('-0.1'))
        self.assertEqual([-0.1], obj.find_floats('a-0.1b'))
        self.assertEqual([-0.1], obj.find_floats('<b>-0.1</b>'))
        self.assertEqual([-0.1], obj.find_floats('a -0.1 b'))

        self.assertEqual([1, 234.567], obj.find_floats('1 23.3.45 234.567'))

        self.assertEqual([1, 234.567, 123], obj.find_floats('1ab23.3,45cd234,567ef123'))

        self.assertEqual([234.567, 234.567], obj.find_floats('<b>234.567</b>234,567'))

        self.assertEqual([], obj.find_floats('1-2'))


if __name__ == '__main__':
    unittest.main()
