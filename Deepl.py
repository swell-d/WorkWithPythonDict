import json
import unittest

import requests

from BaseImport import *


class Deepl:
    __DB = None
    __auth_key = WorkWithJSON.load_dict_from_json('deepl_cfg.txt')['auth_key']
    __DB_PATH = 'deepl_database.txt'

    @classmethod
    def __init__(cls):
        cls.__DB = WorkWithJSON.load_dict_from_json(cls.__DB_PATH)

    @classmethod
    def translate_text(cls, txt, source_lang, target_lang):
        if cls.__DB is None: raise ValueError('use Deepl() instead Deepl')
        text, source_lang, target_lang = Sw.clr(txt), source_lang.upper(), target_lang.upper()
        if not text: return ''
        db = cls.get_db(target_lang)
        if text in db: return db[text]
        page = cls.connect_to_API(text, source_lang, target_lang)
        result = Sw.clr(json.loads(page.text)['translations'][0]['text'])
        cls.save_stat_and_print(text, result, source_lang, target_lang)
        db[text] = result
        cls.save_db()
        return result

    @classmethod
    def save_db(cls):
        WorkWithJSON.save_dict_to_json(cls.__DB, file_name=cls.__DB_PATH)

    @classmethod
    def get_db(cls, target_lang):
        if target_lang not in cls.__DB: cls.__DB[target_lang] = {}
        return cls.__DB[target_lang]

    @classmethod
    def connect_to_API(cls, text, source_lang, target_lang):
        data = {'auth_key': cls.__auth_key,
                'text': text,
                'target_lang': target_lang}
        if source_lang: data['source_lang'] = source_lang
        page = requests.post('https://api.deepl.com/v2/translate', data)
        if page.status_code != 200:
            print(f'translate_text: page status code {page.status_code}')
            print(page.content)
            cls.save_db()
            raise ConnectionError('deepl API problem')
        page.encoding = 'utf-8'
        return page

    @classmethod
    def save_stat_and_print(cls, text, result, source_lang, target_lang):
        if 'summ' not in cls.__DB: cls.__DB['summ'] = 0
        cls.__DB['summ'] += len(text)
        print(f"{source_lang}: {text} ({len(text)})")
        print(f"{target_lang}: {result} ({len(result)})")


class DeeplTests(unittest.TestCase):
    def test_translate(self):
        deepl = Deepl()
        self.assertEqual('Guten Tag!', deepl.translate_text('Hello!', source_lang='EN', target_lang='DE'))


if __name__ == '__main__':
    unittest.main()
