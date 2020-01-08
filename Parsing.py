import codecs
import os
import pathlib
import time
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont
from fake_useragent import UserAgent
from selenium import webdriver

from SwPrint import SwPrint
from TextCorrections import TextCorrections as sw
from parsing_classes import Category
from parsing_classes import Product


# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By


def print(text, only_debug=False, end='\n'):
    SwPrint.print(text, only_debug, end)


class Parsing:
    _driver = None
    _ua = UserAgent()

    @staticmethod
    def check_sku(sku, url, good_symbols=' .-+/'):
        if not sku:
            print(f'=== no sku  {url}')
            return False
        if len(sku) > 21: print(f'=== длинный артикул  {sku} {url}')
        for each in sku:
            if each.isalpha() or each.isdecimal() or each in good_symbols:
                continue
            else:
                print(f'=== спец.символы в артикуле  {sku} {url}')
                return False
        return True

    @classmethod
    def get_logo_with_sku(cls, data, path='images'):
        brand = data['manufacturer']
        sku = data['herstellernummer']
        data['image'] = cls.generate_img(sku, f'{brand}_{sku}', path)
        data['small_image'] = data['image']
        data['thumbnail'] = data['image']
        data['media_gallery'] = data['image']

    @staticmethod
    def generate_img(sku, name, path='images'):
        file_name = f'{sw.good_name(name)}.jpg'
        full_path = f'{path}\\{file_name}'
        if os.path.exists(full_path): return file_name
        print(f'generate img  {sku}')
        fnt = ImageFont.truetype('C:\Windows\Fonts\Arial.ttf', 60)
        img = Image.open('logo.png').convert('RGB')
        d = ImageDraw.Draw(img)
        d.text((60, 880), sku, fill=0, font=fnt)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        img.save(full_path, quality=100, optimize=True, progressive=True)
        return file_name

    @staticmethod
    def create_simple_product(sku, addon, brand, lieferant, name, lang,
                              category_ids, price, am_shipping_type, country, websites, good_symbols=' .-+/'):
        sku = sw.clr(sku).strip(' .,')
        if not Parsing.check_sku(sku, url='simple_product', good_symbols=good_symbols): return None
        addon = sw.clr(addon).upper()
        brand = sw.clr(brand, frst_bg=True)
        name = sw.clr(name, frst_bg=True).strip(' .,')

        data = {}
        data['url'] = 'simple_product'
        data['sku'] = f'{addon} {sku}' if addon else sku
        data['herstellernummer'] = sku
        data['manufacturer'] = brand
        data['lieferant'] = lieferant
        data['name'] = sw.clr(f"{brand} {sku}. {name}").strip(' .,')
        data['short_description'] = name
        data['description'] = name
        Parsing.get_logo_with_sku(data, path=f'images_{lang}')
        data['category_ids'] = category_ids
        for each_cat in data['category_ids'].split('||'):
            cat = Category.create_category(each_cat, None)
            cat.add_product(Product.create_product(data['sku']))
        data['price'] = sw.get_float(price, ndigits=2)

        data['am_shipping_type'] = am_shipping_type if lang != 'ru' else ''
        # 306-Paket 1225-Versand per Spedition 4320-BR
        data['country_of_manufacture'] = country  # DE #US #ES #JP
        data['websites'] = websites  # 'base'

        Parsing.same_for_all(data, lang)
        Parsing.minimalka(data)

        # additional
        # data['special_price'] = ''
        # data['weight'] = ''
        # data['ean'] = ''
        # data['delivery_time'] = ''
        # data['relation'] = ''  # через ||

        return data

    @staticmethod
    def same_for_all(data, lang):
        url_key = f"{data['manufacturer']}_{data['herstellernummer']}".strip('_').lower()
        url_key = url_key.replace('/', '-').replace('\\', '-').replace(' ', '-').replace('+', '-').replace('.', '-')
        data['url_key'] = quote(url_key)
        data['status'] = 1
        data['qty'] = 1000
        data['is_in_stock'] = 1
        data['tax_class_id'] = 'Vollbesteuerte Artikel' if lang != 'ru' else ''
        data['attribute_set_name'] = 'Default' if lang != 'ru' else ''

    @staticmethod
    def minimalka(data):
        min_count = int(data.get('qty_increments', 1))
        data['enable_qty_increments'] = 1 if min_count > 1 else 0
        data['use_config_enable_qty_inc'] = 0 if min_count > 1 else 1
        data['qty_increments'] = min_count
        data['use_config_qty_increments'] = 0 if min_count > 1 else 1

    @staticmethod
    def reorganize_categories(lang):
        ### работаем с категориями
        col = 1
        new_cat_name = None
        print(f'всего {Category.count() / col} категорий')
        while True:
            a, b = 0, 0
            for each in list(Category.categories.values()).copy():
                if str(each).count('|') < 3: continue
                ### удаляем папки с количеством товаров меньше 3
                if each.children_categories_count == 0 and each.children_products_count < 3:
                    each.delete()
                    a += 1
                ### удаляем промежуточные папки без товаров
                elif each.children_categories_count == 1 and each.children_products_count == 0:
                    each.delete()
                    b += 1
            if a or b: print(f'удалено {a / col}+{b / col} категорий')
            if (a + b) == 0: break
        print(f'всего {Category.count() // col} категорий')
        ### перемещаем "промежуточные" товары в новую папку Other
        c = 0
        for each in list(Category.categories.values()).copy():
            if each.children_categories_count > 0 and each.children_products_count > 0:
                if lang == 'de':
                    new_cat_name = 'Zubehör'
                elif lang == 'en':
                    new_cat_name = 'Other'
                elif lang == 'ru':
                    new_cat_name = 'Прочее'
                new_cat = Category.create_category(f'{each}|{new_cat_name}')
                for child in each.find_children(show_cats=False, show_products=True, text=False):
                    child.move(each, new_cat)
                c += 1
        if new_cat_name:
            print(f'создано {c // col} новых категорий {new_cat_name}. итого {Category.count() // col} категорий')

    @classmethod
    def get_htmls(cls, url, simple=False):  # скачиваем страницу. если уже скачана, берём сохранённую копию
        result = []
        file_name = sw.get_cache_path(url)
        if os.path.exists(file_name):
            print(f'use exist  {url}', only_debug=True)
            result.append(cls.read_file(file_name))
            i = 1
            while True:
                file_name_dop = f'{file_name}_{i + 1}.html'
                if not os.path.exists(file_name_dop): break
                print(f'use exist dop  {file_name_dop}', only_debug=True)
                result.append(cls.read_file(file_name_dop))
                i += 1
        else:
            print(f'download  {url}')
            if simple:
                result.append(cls.get_simple_html(url, file_name))
            else:
                result.append(cls.get_htmls_from_webdriver(url, file_name))
        return result

    @classmethod
    def create_web_driver(cls, url):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        cls._driver = webdriver.Chrome('C:\\Users\\Administrator\\Documents\\_python\\chromedriver.exe',
                                       chrome_options=chrome_options)
        cls._driver.implicitly_wait(10)
        cls._driver.get(url)
        input('продолжить?')
        print('дальше')

    @staticmethod
    def read_file(file_name):
        with codecs.open(file_name, 'r', 'utf-8') as file:
            return file.read()

    @staticmethod
    def save_text_to_file(file_name, text):
        pathlib.Path(file_name[:file_name.rfind('\\')]).mkdir(parents=True, exist_ok=True)
        with codecs.open(file_name, 'w', 'utf-8') as f:
            f.write(text)

    @classmethod
    def get_simple_html(cls, url, file_name):
        headers = {'User-Agent': cls._ua.chrome}
        try:
            html = requests.get(url, headers=headers)
        except:
            try:
                html = requests.get(url, headers=headers)
            except:
                print(f'=== ошибка скачивания  {url}')
                return ''
        if html.status_code == 404:
            print(f'=== 404  {url}')
            return ''
        html.encoding = 'utf-8'
        html_text = html.text
        cls.save_text_to_file(file_name, html_text)
        return html_text

    @classmethod
    def get_htmls_from_webdriver(cls, url, file_name):
        if not cls._driver: cls.create_web_driver(url)
        try:
            cls._driver.get(url)
        except:
            try:
                cls._driver.get(url)
            except:
                print(f'=== ошибка скачивания  {url}')
                return ''
        time.sleep(1)
        html_text = cls._driver.page_source
        cls.save_text_to_file(file_name, html_text)
        return html_text

    @staticmethod
    def delete_file(url):
        file_name = sw.get_cache_path(url)
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f'=== delete file  {url}')
        else:
            print(f'=== file not found  {url}')
