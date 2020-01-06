import re
import unittest


class TextCorrections:
    @classmethod
    def clr(cls, text, frst_bg=False):
        result = re.sub(r'\s+', ' ', str(text)).strip() if text is not None else ''
        return result if not frst_bg else cls.first_big(result)

    @staticmethod
    def first_big(text):
        # if not isinstance(text, str): raise ValueError
        return text[0].upper() + text[1:] if text else ''

    @staticmethod
    def get_float(text, ndigits=2):
        # if not isinstance(text, [str, int, float]): raise ValueError
        if isinstance(text, str): text = text.replace(',', '.')
        return round(float(text), ndigits)


class FindDigits:
    def __init__(self, point='.,'):
        self.__SS = f'[^0-9{point}-]'
        self.__float_compile = re.compile(
            f"{self.__SS}(0){self.__SS}|{self.__SS}(-?0[{point}]\\d+){self.__SS}|{self.__SS}(-?[1-9]\\d*([{point}]\\d+)?){self.__SS}")

    def find_digits(self, text):
        findall = re.findall(self.__float_compile, f" {str(text)} ")
        result = []
        for each in findall: result.append(float((each[2] or each[1] or each[0]).replace(',', '.')))
        return result if result else ['']


class TextCorrectionsTests(unittest.TestCase):
    def test_clr(self):
        obj = TextCorrections()
        self.assertEqual('', obj.clr(' '))
        self.assertEqual('', obj.clr('\n'))
        self.assertEqual('1 1', obj.clr(' 1  \n  1 '))
        self.assertEqual('None', obj.clr('None'))
        self.assertEqual('', obj.clr(None))

    def test_first_big(self):
        obj = TextCorrections()
        self.assertEqual('', obj.first_big(''))
        self.assertEqual('A', obj.first_big('a'))
        self.assertEqual('Aa', obj.first_big('aa'))

    def test_digits(self):
        obj = FindDigits()
        self.assertEqual('', obj.find_digits('')[0])
        self.assertEqual('', obj.find_digits(' ')[0])
        self.assertEqual('', obj.find_digits('abc')[0])
        self.assertEqual(0, obj.find_digits(0)[0])

        self.assertEqual(0, obj.find_digits('0')[0])
        self.assertEqual(0, obj.find_digits('a0b')[0])
        self.assertEqual(0, obj.find_digits('<b>0</b>')[0])
        self.assertEqual(0, obj.find_digits('a 0 b')[0])

        self.assertEqual(1, obj.find_digits('1')[0])
        self.assertEqual(1, obj.find_digits('a1b')[0])
        self.assertEqual(1, obj.find_digits('<b>1</b>')[0])
        self.assertEqual(1, obj.find_digits('a 1 b')[0])

        self.assertEqual(-1, obj.find_digits('-1')[0])
        self.assertEqual(-1, obj.find_digits('a-1b')[0])
        self.assertEqual(-1, obj.find_digits('<b>-1</b>')[0])
        self.assertEqual(-1, obj.find_digits('a -1 b')[0])

        self.assertEqual(0.1, obj.find_digits('0.1')[0])
        self.assertEqual(0.1, obj.find_digits('a0.1b')[0])
        self.assertEqual(0.1, obj.find_digits('<b>0.1</b>')[0])
        self.assertEqual(0.1, obj.find_digits('a 0.1 b')[0])

        self.assertEqual(-0.1, obj.find_digits('-0.1')[0])
        self.assertEqual(-0.1, obj.find_digits('a-0.1b')[0])
        self.assertEqual(-0.1, obj.find_digits('<b>-0.1</b>')[0])
        self.assertEqual(-0.1, obj.find_digits('a -0.1 b')[0])

        self.assertEqual(1, obj.find_digits('1 23.3.45 234.567')[0])
        self.assertEqual(234.567, obj.find_digits('1 23.3.45 234.567')[1])

        self.assertEqual(1, obj.find_digits('1ab23.3,45cd234,567ef123')[0])
        self.assertEqual(234.567, obj.find_digits('1ab23.3,45cd234,567ef123')[1])
        self.assertEqual(123, obj.find_digits('1ab23.3,45cd234,567ef123')[2])

        self.assertEqual(234.567, obj.find_digits('<b>234.567</b>123')[0])
        self.assertEqual(123, obj.find_digits('<b>234.567</b>123')[1])

        self.assertEqual('', obj.find_digits('1-2')[0])


if __name__ == '__main__':
    unittest.main()
