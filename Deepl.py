import json
import unittest

import requests

from BaseImport import *


class Deepl:
    __DB = None
    __auth_key = WorkWithJSON.load_dict_from_json('deepl_cfg.txt')['auth_key']

    @classmethod
    def __init__(cls):
        cls.__DB = WorkWithJSON.load_dict_from_json('deepl_database.txt')

    @classmethod
    def translate_text(cls, txt, source_lang, target_lang):
        if cls.__DB is None: raise ValueError('use Deepl() instead Deepl')
        text = Sw.clr(txt)
        if not text: return ''
        source_lang, target_lang = source_lang.upper(), target_lang.upper()
        if target_lang not in cls.__DB: cls.__DB[target_lang] = {}
        db = cls.__DB[target_lang]
        if text in db: return db[text]

        data = {'auth_key': cls.__auth_key,
                'text': text,
                'target_lang': target_lang}
        if source_lang: data['source_lang'] = source_lang
        page = requests.post('https://api.deepl.com/v2/translate', data)
        if page.status_code != 200:
            print(f'translate_text: page status code {page.status_code}')
            print(page.content)
            WorkWithJSON.save_dict_to_json(cls.__DB, file_name='deepl_database.txt')
            raise ConnectionError('deepl API problem')
        page.encoding = 'utf-8'

        result = Sw.clr(json.loads(page.text)['translations'][0]['text'])
        if 'summ' not in cls.__DB: cls.__DB['summ'] = 0
        cls.__DB['summ'] += len(text)
        print(f"{source_lang}: {text} ({len(text)})")
        print(f"{target_lang}: {result} ({len(result)})")
        db[text] = result
        WorkWithJSON.save_dict_to_json(cls.__DB, file_name='deepl_database.txt')
        return result


class DeeplTests(unittest.TestCase):
    def test_translate(self):
        deepl = Deepl()
        self.assertEqual('Guten Tag!', deepl.translate_text('Hello!', source_lang='EN', target_lang='DE'))


if __name__ == '__main__':
    unittest.main()
