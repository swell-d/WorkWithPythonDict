import re
import unittest


class CheckTypes:
    @classmethod
    def return_int_str(cls, text):
        text = str(text)
        if cls.isint(text): return int(text)
        return text

    @classmethod
    def return_int_float_str(cls, text):
        text = str(text)
        if cls.isint(text): return int(text)
        if cls.isfloat(text.replace(',', '.')): return float(text.replace(',', '.'))
        return text


class CheckTypesRe(CheckTypes):
    __int_compile = re.compile("^0$|^-?[1-9]\\d*$")
    __float_compile = re.compile("^0$|^-?0[.]\\d+$|^-?[1-9]\\d*([.]\\d+)?$")

    @classmethod
    def isint(cls, text):
        return True if re.match(cls.__int_compile, str(text)) else False

    @classmethod
    def isfloat(cls, text):
        if len(str(text)) > 17: return False
        return True if re.match(cls.__float_compile, str(text)) else False


class CheckTypesTry(CheckTypes):
    @staticmethod
    def isint(text):
        try: return str(int(text)) == str(text)
        except: return False

    @staticmethod
    def isfloat(text):
        try:
            text = str(text)
            if text == '-0': return False
            return str(float(text)) == (text if '.' in text else f'{text}.0')
        except:
            return False


class CheckTypesTests(unittest.TestCase):
    def test_int(self, cl=None):
        if cl is None: return
        good_values = ['-1', '0', '1']
        bad_values = ['', ' ', '-', '+', '00', '01', '0123', '-0', '-00', '-01', '-0123', ' 1', '1.']
        for val in good_values:
            self.assertTrue(cl.isint(val), msg=val)
        for val in bad_values:
            self.assertFalse(cl.isint(val), msg=val)

    def test_float(self, cl=None):
        if cl is None: return
        good_values = ['-1', '0', '1', '-1.0', '1.0', '-0.1', '0.1', '911', '0.001']
        bad_values = ['', ' ', '-', '+', '00', '01', '0123', '-0', '-00', '-01', '-0123',
                      '00.0', '01.', '-01.', '.1', '-.1', '1-', ' 1', '1 ', '-001',
                      '0.1.1', '1..1', '0..1', '23.3.4']
        for val in good_values:
            self.assertTrue(cl.isfloat(val), msg=val)
        for val in bad_values:
            self.assertFalse(cl.isfloat(val), msg=val)

    def testRe(self):
        self.test_int(CheckTypesRe)
        self.test_float(CheckTypesRe)

    def testTry(self):
        self.test_int(CheckTypesTry)
        self.test_float(CheckTypesTry)


if __name__ == '__main__':
    unittest.main()