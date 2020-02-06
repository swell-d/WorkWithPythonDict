import re
import unittest


class FindDigits:
    point = '.,'
    __ss = f'[^0-9{point}-]'
    __float_compile = re.compile(
        f"{__ss}(0){__ss}|{__ss}(-?0[{point}]\\d+){__ss}|{__ss}(-?[1-9]\\d*([{point}]\\d+)?){__ss}")

    @classmethod
    def find_int(cls, text):
        findall = re.findall(cls.__float_compile, f" {str(text)} ")
        result = []
        for each in findall: result.append(int((each[2] or each[1] or each[0]).replace(',', '.')))
        return result if result else ['']

    @classmethod
    def find_floats(cls, text):
        findall = re.findall(cls.__float_compile, f" {str(text)} ")
        result = []
        for each in findall: result.append(float((each[2] or each[1] or each[0]).replace(',', '.')))
        return result if result else ['']


class FindDigitsTests(unittest.TestCase):
    def test_digits(self):
        obj = FindDigits()
        self.assertEqual('', obj.find_floats('')[0])
        self.assertEqual('', obj.find_floats(' ')[0])
        self.assertEqual('', obj.find_floats('abc')[0])
        self.assertEqual(0, obj.find_floats(0)[0])

        self.assertEqual(0, obj.find_floats('0')[0])
        self.assertEqual(0, obj.find_floats('a0b')[0])
        self.assertEqual(0, obj.find_floats('<b>0</b>')[0])
        self.assertEqual(0, obj.find_floats('a 0 b')[0])

        self.assertEqual(1, obj.find_floats('1')[0])
        self.assertEqual(1, obj.find_floats('a1b')[0])
        self.assertEqual(1, obj.find_floats('<b>1</b>')[0])
        self.assertEqual(1, obj.find_floats('a 1 b')[0])

        self.assertEqual(-1, obj.find_floats('-1')[0])
        self.assertEqual(-1, obj.find_floats('a-1b')[0])
        self.assertEqual(-1, obj.find_floats('<b>-1</b>')[0])
        self.assertEqual(-1, obj.find_floats('a -1 b')[0])

        self.assertEqual(0.1, obj.find_floats('0.1')[0])
        self.assertEqual(0.1, obj.find_floats('a0.1b')[0])
        self.assertEqual(0.1, obj.find_floats('<b>0.1</b>')[0])
        self.assertEqual(0.1, obj.find_floats('a 0.1 b')[0])

        self.assertEqual(-0.1, obj.find_floats('-0.1')[0])
        self.assertEqual(-0.1, obj.find_floats('a-0.1b')[0])
        self.assertEqual(-0.1, obj.find_floats('<b>-0.1</b>')[0])
        self.assertEqual(-0.1, obj.find_floats('a -0.1 b')[0])

        self.assertEqual(1, obj.find_floats('1 23.3.45 234.567')[0])
        self.assertEqual(234.567, obj.find_floats('1 23.3.45 234.567')[1])

        self.assertEqual(1, obj.find_floats('1ab23.3,45cd234,567ef123')[0])
        self.assertEqual(234.567, obj.find_floats('1ab23.3,45cd234,567ef123')[1])
        self.assertEqual(123, obj.find_floats('1ab23.3,45cd234,567ef123')[2])

        self.assertEqual(234.567, obj.find_floats('<b>234.567</b>123')[0])
        self.assertEqual(123, obj.find_floats('<b>234.567</b>123')[1])

        self.assertEqual('', obj.find_floats('1-2')[0])


if __name__ == '__main__':
    unittest.main()
