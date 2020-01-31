import json
import unittest

import requests

import Sw
import WorkWithJSON


class Deepl:
    __PATH = 'C:\\Users\\Administrator\\Documents\\_python\\_pycharm\\WorkWithPythonDict\\'
    __AUTH_KEY = WorkWithJSON.load_dict_from_json(f'{__PATH}deepl_cfg.txt')['auth_key']
    __DB_PATH = f'{__PATH}deepl_database.txt'
    __DB = WorkWithJSON.load_dict_from_json(__DB_PATH)

    def __init__(self, personal_dict=None):
        self.__personal_dict = personal_dict.copy() if personal_dict is not None else {}

    def translate(self, txt, source_lang, target_lang):
        text, source_lang, target_lang = Sw.clr(txt), source_lang.upper(), target_lang.upper()
        if not text: return ''
        db = self.__get_db(target_lang)
        if text in db:
            result = db[text]
            result = self.__check_personal_dict(result)
        else:
            page = self.__connect_to_API(text, source_lang, target_lang)
            result = Sw.clr(json.loads(page.text)['translations'][0]['text'])
            result = self.__check_personal_dict(result)
            self.__save_stat_and_print(text, result, source_lang, target_lang)
            db[text] = result
            self.__save_db()
        return result

    def __check_personal_dict(self, result):
        for key, value in self.__personal_dict.items():
            result = result.replace(key, value)
        return result

    @classmethod
    def __save_db(cls):
        WorkWithJSON.save_dict_to_json(cls.__DB, file_name=cls.__DB_PATH)

    @classmethod
    def __get_db(cls, target_lang):
        if target_lang not in cls.__DB: cls.__DB[target_lang] = {}
        return cls.__DB[target_lang]

    @classmethod
    def __connect_to_API(cls, text, source_lang, target_lang):
        data = {'auth_key': cls.__AUTH_KEY,
                'text': text,
                'target_lang': target_lang,
                'tag_handling': 'xml'}
        if source_lang: data['source_lang'] = source_lang
        page = requests.post('https://api.deepl.com/v2/translate', data)
        if page.status_code != 200:
            print(f'translate_text: page status code {page.status_code}')
            print(page.content)
            cls.__save_db()
            raise ConnectionError('deepl API problem')
        page.encoding = 'utf-8'
        return page

    @classmethod
    def __save_stat_and_print(cls, text, result, source_lang, target_lang):
        if 'summ' not in cls.__DB: cls.__DB['summ'] = 0
        cls.__DB['summ'] += len(text)
        print(f"{source_lang}: {text} ({len(text)})")
        print(f"{target_lang}: {result} ({len(result)})")


class DeeplTests(unittest.TestCase):
    def test_translate(self):
        self.assertEqual(
            'Guten Tag!',
            Deepl().translate('Hello!', source_lang='EN', target_lang='DE')
        )
        self.assertEqual(
            'Drücken Sie auf <i>Weiter</i>, um zur nächsten Seite zu gelangen.',
            Deepl().translate('Press <i>Continue</i> to advance to the next page.', source_lang='EN', target_lang='DE')
        )


if __name__ == '__main__':
    unittest.main()
