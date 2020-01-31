import re
import unittest
from abc import ABC, abstractmethod


class CheckTypes(ABC):
    def return_int_or_str(self, txt):
        text = str(txt)
        if self.isint(text): return int(text)
        return text

    def return_int_float_str(self, txt):
        text = str(txt)
        if self.isint(text): return int(text)
        if self.isfloat(text.replace(',', '.')): return float(text.replace(',', '.'))
        return text

    @abstractmethod
    def isint(self, txt):
        pass

    @abstractmethod
    def isfloat(self, txt):
        pass


class CheckTypesRe(CheckTypes):
    __int_compile = re.compile("^0$|^-?[1-9]\\d*$")
    __float_compile = re.compile("^0$|^-?0[.]\\d+$|^-?[1-9]\\d*([.]\\d+)?$")

    def isint(self, txt):
        text = str(txt)
        return True if re.match(self.__int_compile, text) else False

    def isfloat(self, txt):
        text = str(txt)
        if len(text) > 17: return False
        return True if re.match(self.__float_compile, text) else False


class CheckTypesTry(CheckTypes):
    def isint(self, txt):
        try:
            text = str(txt)
            return str(int(text)) == text
        except:
            return False

    def isfloat(self, txt):
        try:
            text = str(txt)
            if text == '-0': return False
            return str(float(text)) == (text if '.' in text else f'{text}.0')
        except:
            return False


class CheckTypesTests(unittest.TestCase):
    def test_int(self, obj=None):
        if obj is None: return
        good_values = ['-1', '0', '1']
        bad_values = ['', ' ', '-', '+', '00', '01', '0123', '-0', '-00', '-01', '-0123', ' 1', '1.']
        for val in good_values:
            self.assertTrue(obj.isint(val), msg=val)
        for val in bad_values:
            self.assertFalse(obj.isint(val), msg=val)

    def test_float(self, obj=None):
        if obj is None: return
        good_values = ['-1', '0', '1', '-1.0', '1.0', '-0.1', '0.1', '911', '0.001']
        bad_values = ['', ' ', '-', '+', '00', '01', '0123', '-0', '-00', '-01', '-0123',
                      '00.0', '01.', '-01.', '.1', '-.1', '1-', ' 1', '1 ', '-001',
                      '0.1.1', '1..1', '0..1', '23.3.4']
        for val in good_values:
            self.assertTrue(obj.isfloat(val), msg=val)
        for val in bad_values:
            self.assertFalse(obj.isfloat(val), msg=val)

    def testRe(self):
        self.test_int(CheckTypesRe())
        self.test_float(CheckTypesRe())

    def testTry(self):
        self.test_int(CheckTypesTry())
        self.test_float(CheckTypesTry())


if __name__ == '__main__':
    unittest.main()
