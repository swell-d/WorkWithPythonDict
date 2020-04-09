import re
import unittest
import urllib.parse


def clr(text, start_with_big=False):
    result = re.sub(r'\s+', ' ', str(text)).strip() if text is not None else ''
    return result if not start_with_big else first_big(result)


def first_big(text):
    # if not isinstance(text, str): raise ValueError
    return text[0].upper() + text[1:] if text else ''


def get_float(text, ndigits=2):
    if isinstance(text, str): text = text.replace(',', '.')
    return round(float(text), ndigits)


def get_float_or_empty(text, ndigits=2):
    if clr(text) == '': return ''
    return get_float(text, ndigits)


def get_float_or_null(text, ndigits=2):
    if not text: return 0.0
    return get_float(text, ndigits)


def good_name(name):
    name = name.replace('/', '-').replace('\\', '-').replace(' ', '_').replace('*', '-')
    name = name.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    name = name.replace('°', '').replace('+', '-').replace('?', '-').replace('&', '-').replace('%20', '_')
    # name = transliterate(name)
    return urllib.parse.quote(name).lower()


def get_cache_path(url, short=False, html=False, cache_path='C:\\_cache\\'):
    if cache_path[-1] != '\\': cache_path += '\\'
    file_name = url[url.find("//") + 2:].replace('..', '').replace('/', '\\')
    if short and '?' in file_name: file_name = file_name[:file_name.rfind("?")]
    file_name = urllib.parse.quote(file_name, safe='\\')
    if file_name[-1] == '\\': file_name += 'html.html' if html else 'file'
    if html:
        if '\\' not in file_name: file_name += '\\html.html'
        right_part = file_name[file_name.rfind('\\'):]
        if '.' not in right_part: file_name += '.html'
    return re.sub('\\\\+', '\\\\', cache_path + file_name).lower()


def fuck_rus_letters(text):
    text = str(text)
    rus = 'УКЕНХВАРОСМТукехаросм'
    eng = 'YKEHXBAPOCMTykexapocm'
    for i, each in enumerate(rus):
        text = re.sub(each, eng[i], text)
    return text


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


class SwTests(unittest.TestCase):
    def test_clr(self):
        self.assertEqual('', clr(' '))
        self.assertEqual('', clr('\n'))
        self.assertEqual('1 1', clr(' 1  \n  1 '))
        self.assertEqual('None', clr('None'))
        self.assertEqual('', clr(None))

    def test_first_big(self):
        self.assertEqual('', first_big(''))
        self.assertEqual('A', first_big('a'))
        self.assertEqual('Aa', first_big('aa'))


if __name__ == '__main__':
    unittest.main()
