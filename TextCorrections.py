import re
import unittest
from urllib.parse import quote


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
        if isinstance(text, str): text = text.replace(',', '.')
        return round(float(text), ndigits)

    @classmethod
    def get_float_or_empty(cls, text, ndigits=2):
        if cls.clr(text) == '': return ''
        return cls.get_float(text, ndigits)

    @classmethod
    def get_float_or_null(cls, text, ndigits=2):
        if not text: return 0.0
        return cls.get_float(text, ndigits)

    @classmethod
    def good_name(cls, name):
        name = name.replace('/', '-').replace('\\', '-').replace(' ', '-').replace('*', '-')
        name = name.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
        name = name.replace('°', '').replace('+', '-').replace('?', '-').replace('&', '-').replace('%20', '_')
        # name = cls.transliterate(name)
        return quote(name).lower()

    @staticmethod
    def get_cache_path(url, short=False, html=False,
                       cache_path='C:\\Users\\Administrator\\Documents\\_python\\_cache\\'):
        if cache_path[-1] != '\\': cache_path += '\\'
        file_name = url[url.find("//") + 2:].replace('..', '').replace('/', '\\')
        if short and '?' in file_name: file_name = file_name[:file_name.rfind("?")]
        file_name = quote(file_name, safe='\\')
        if file_name[-1] == '\\': file_name += 'html.html' if html else 'file'
        if html:
            if '\\' not in file_name: file_name += '\\html.html'
            right_part = file_name[file_name.rfind('\\'):]
            if '.' not in right_part: file_name += '.html'
        return re.sub('\\\\+', '\\\\', cache_path + file_name).lower()

    @staticmethod
    def fuck_rus_letters(text):
        text = str(text)
        rus = 'УКЕНХВАРОСМТукехаросм'
        eng = 'YKEHXBAPOCMTykexapocm'
        for i, each in enumerate(rus):
            text = re.sub(each, eng[i], text)
        return text

    @staticmethod
    def transliterate(string):
        capital_letters = {u'А': u'A',
                           u'Б': u'B',
                           u'В': u'V',
                           u'Г': u'G',
                           u'Д': u'D',
                           u'Е': u'E',
                           u'Ё': u'E',
                           u'Ж': u'Zh',
                           u'З': u'Z',
                           u'И': u'I',
                           u'Й': u'Y',
                           u'К': u'K',
                           u'Л': u'L',
                           u'М': u'M',
                           u'Н': u'N',
                           u'О': u'O',
                           u'П': u'P',
                           u'Р': u'R',
                           u'С': u'S',
                           u'Т': u'T',
                           u'У': u'U',
                           u'Ф': u'F',
                           u'Х': u'H',
                           u'Ц': u'Ts',
                           u'Ч': u'Ch',
                           u'Ш': u'Sh',
                           u'Щ': u'Sch',
                           u'Ъ': u'',
                           u'Ы': u'Y',
                           u'Ь': u'',
                           u'Э': u'E',
                           u'Ю': u'Yu',
                           u'Я': u'Ya', }
        lower_case_letters = {u'а': u'a',
                              u'б': u'b',
                              u'в': u'v',
                              u'г': u'g',
                              u'д': u'd',
                              u'е': u'e',
                              u'ё': u'e',
                              u'ж': u'zh',
                              u'з': u'z',
                              u'и': u'i',
                              u'й': u'y',
                              u'к': u'k',
                              u'л': u'l',
                              u'м': u'm',
                              u'н': u'n',
                              u'о': u'o',
                              u'п': u'p',
                              u'р': u'r',
                              u'с': u's',
                              u'т': u't',
                              u'у': u'u',
                              u'ф': u'f',
                              u'х': u'h',
                              u'ц': u'ts',
                              u'ч': u'ch',
                              u'ш': u'sh',
                              u'щ': u'sch',
                              u'ъ': u'',
                              u'ы': u'y',
                              u'ь': u'',
                              u'э': u'e',
                              u'ю': u'yu',
                              u'я': u'ya', }
        translit_string = ""
        for index, char in enumerate(string):
            if char in lower_case_letters.keys():
                char = lower_case_letters[char]
            elif char in capital_letters.keys():
                char = capital_letters[char]
                if len(string) > index + 1:
                    if string[index + 1] not in lower_case_letters.keys():
                        char = char.upper()
                else:
                    char = char.upper()
            translit_string += char
        return translit_string


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


class Html:
    @staticmethod
    def div_title(text, m2=False):
        if not m2: return f'<br><br><div class="section-title">{str(text)}</div>' if text else ''
        return f'<br><br><div class="section-title"><strong>{str(text)}</strong></div>' if text else ''

    @staticmethod
    def div_ul_start():
        return '<ul class="bullet">'

    @staticmethod
    def div_li(text, link=None):
        if text and link:
            return f'<li><a href="{link}" target="_blank">{text}</a></li>'
        elif text:
            return f'<li>{text}</li>'
        return ''

    @staticmethod
    def div_ul_end():
        return '</ul>'

    @staticmethod
    def div_youtube(video_link):
        if not video_link: return ''
        return f'<iframe width="800" height="450" src="https://www.youtube-nocookie.com/embed/{video_link}" ' \
               f'frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" ' \
               f'allowfullscreen></iframe><br><br>'


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
