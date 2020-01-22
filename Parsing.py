import codecs
import os
import pathlib
import time
from shutil import copyfile
from urllib.parse import quote, unquote, urljoin

import requests
import urllib3
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver

import Category
import Product
from GlobalFunctions import print, generate_time_string
from SwPrint import SwPrint
from TextCorrections import TextCorrections as Sw


# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By


class Parsing:
    _driver = None
    _headers = {'User-Agent': UserAgent().chrome}

    @staticmethod
    def check_sku(sku, url, good_symbols=' .-+/'):
        if not sku:
            print(f'=== no sku  {url}')
            return False
        # if len(sku) > 21: print(f'=== длинный артикул  {sku} {url}')
        for each in sku:
            if each.isalpha() or each.isdecimal() or each in good_symbols:
                continue
            else:
                print(f'=== спец.символы в артикуле  {sku} {url}')
                return False
        return True

    @classmethod
    def create_simple_product(cls, sku, addon, brand, lieferant, name, lang, imgs,
                              category_ids, price, am_shipping_type, country, websites, good_symbols=' .-+/'):
        sku = Sw.clr(sku).strip(' .,')
        if not cls.check_sku(sku, url='simple_product', good_symbols=good_symbols): return None
        addon = Sw.clr(addon).upper()
        brand = Sw.clr(brand, frst_bg=True)
        name = Sw.clr(name, frst_bg=True).strip(' .,')

        data = {}
        data['url'] = 'simple_product'
        data['sku'] = f'{addon} {sku}' if addon else sku
        data['herstellernummer'] = sku
        data['manufacturer'] = brand
        data['lieferant'] = lieferant
        data['name'] = Sw.clr(f"{brand} {sku}. {name}").strip(' .,')
        data['short_description'] = name
        data['description'] = name
        cls.download_imgs(data, imgs=imgs, path='images')
        # data['category_ids'] = category_ids
        for each_category in category_ids.split('||'):
            cls.create_product_and_category(data['sku'], each_category)
        data['price'] = Sw.get_float(price, ndigits=2) if price else 0

        data['am_shipping_type'] = am_shipping_type if lang != 'ru' else ''
        # 306-Paket 1225-Versand per Spedition 4320-BR
        data['country_of_manufacture'] = country  # DE #US #ES #JP
        data['websites'] = websites  # 'base'

        cls.same_for_all(data, lang)
        # cls.minimalka(data)

        # additional
        # data['special_price'] = ''
        # data['weight'] = ''
        # data['ean'] = ''
        # data['delivery_time'] = ''
        # data['relation'] = ''  # через ||

        return data

    @classmethod
    def create_product_and_category(cls, sku, category_path):
        category = Category.Category.create_category(category_path, None)
        category.add_product(Product.Product.create_product(sku))

    @classmethod
    def get_good_html(cls, text):
        if text == '': return ''
        return Sw.clr(BeautifulSoup(text, 'lxml').body)[6:-7]

    @staticmethod
    def same_for_all(data, lang):
        brand = Sw.transliterate(data['manufacturer'])
        sku = Sw.transliterate(data['herstellernummer'])
        url_key = f"{brand}_{sku}".strip('_').lower()
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
    def reorganize_categories(products, lang, col=1):
        Category.Category.reorganize_categories(lang, col)
        for product in products.values():
            product['category_ids'] = Product.Product.export_categories(product['sku'])
        Category.Category.clear()
        Product.Product.clear()

    @classmethod
    def get_htmls_from_web(cls, url, simple=False, additional_func=None):
        result = []
        file_name = Sw.get_cache_path(url, html=True)
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
                result.append(cls.get_htmls_from_webdriver(url, file_name, additional_func))
        return result

    @classmethod
    def _create_web_driver(cls, url):
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
        if '\\' in file_name: pathlib.Path(file_name[:file_name.rfind('\\')]).mkdir(parents=True, exist_ok=True)
        with codecs.open(file_name, 'w', 'utf-8') as f:
            f.write(text)

    @classmethod
    def download(cls, url):
        try:
            page = requests.get(url, headers=cls._headers)
        except:
            time.sleep(1)
            try:
                page = requests.get(url, headers=cls._headers)
            except:
                print(f'=== download error  {url}')
                return None
        if page.status_code != 200:
            print(f'=== page status code {page.status_code} for  {url}')
            return None
        return page

    @classmethod
    def get_simple_html(cls, url, file_name):
        page = cls.download(url)
        if page is None: return ''
        page.encoding = 'utf-8'
        cls.save_text_to_file(file_name, page.text)
        return page.text

    @classmethod
    def get_htmls_from_webdriver(cls, url, file_name, additional_func=None):
        if not cls._driver: cls._create_web_driver(url)
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
        if additional_func is not None:
            additional_func(cls._driver)
            html_text = cls._driver.page_source
        cls.save_text_to_file(file_name, html_text)
        return html_text

    @classmethod
    def get_file_from_web(cls, url, name, path='images'):
        if not name: name = unquote(url[url.rfind('/') + 1:url.rfind('.')])
        name = Sw.good_name(name)
        cache_path = Sw.get_cache_path(url)
        right_part = url[url.rfind('/') + 1:]
        if '?' in right_part: right_part = right_part[:right_part.rfind('?')]
        file_type = right_part[right_part.rfind('.'):].lower() if '.' in right_part else ''
        if file_type == '.jpeg': file_type = '.jpg'
        if 'treston' in path and not file_type: file_type = '.pdf'
        if len(file_type) > 4 or not file_type:
            print(f'=== bad file_type "{file_type}" in url  {url}')
            raise ValueError
        new_path = f'{path}\\{name}{file_type}'
        if os.path.exists(cache_path) and os.path.exists(new_path):
            if os.stat(cache_path).st_size == os.stat(new_path).st_size:
                print(f'do nothing  {url}', only_debug=True)
            else:
                # print(f'st_size: {os.stat(cache_path).st_size} != {os.stat(new_path).st_size}')
                if cls._copyfile(url, cache_path, new_path, file_type, path) is None: return ''
        elif os.path.exists(cache_path) and not os.path.exists(new_path):
            if cls._copyfile(url, cache_path, new_path, file_type, path) is None: return ''
        else:
            print(f'download file  {url}')
            urllib3.disable_warnings()
            page = cls.download(url)
            if page is None: return ''
            if '\\' in cache_path: pathlib.Path(cache_path[:cache_path.rfind('\\')]).mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'wb') as file:
                file.write(page.content)
            if cls._copyfile(url, cache_path, new_path, file_type, path) is None: return ''
        return new_path.replace(f'{path}\\', '').lower()

    @classmethod
    def _copyfile(cls, url, cache_path, new_path, file_type, path):
        if os.stat(cache_path).st_size == 0: return None  # Todo try to download one more time
        if 'images' in path and file_type in ['.jpg', '.png', '.gif']:
            img = Image.open(cache_path)
            if (img.size[0] + img.size[1]) < 200: return None
        print(f'copy file  {url}', only_debug=True)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        copyfile(cache_path, new_path)
        return True

    @classmethod
    def download_imgs(cls, data, imgs, path='images'):
        i = 1
        brand = Sw.transliterate(data['manufacturer'])
        sku = Sw.transliterate(data['herstellernummer'])
        for link in imgs:
            if not data.get('image'):
                data['image'] = cls.get_file_from_web(link, f'{brand}_{sku}', path)
                data['image'] = data['image'].replace('png', 'jpg').replace('gif', 'jpg').replace('jpeg', 'jpg')
                if not data['image']: continue
                data['small_image'] = data['image']
                data['thumbnail'] = data['image']
                data['media_gallery'] = data['image']
            else:
                next_img = cls.get_file_from_web(link, f'{brand}_{sku}_{i + 1}', path)
                if not next_img: continue
                i += 1
                data['media_gallery'] += f'|{next_img}'
        if not data.get('image'): cls.get_logo_with_sku(data, f'{path}_logos')

    @classmethod
    def get_logo_with_sku(cls, data, path='images'):
        brand = Sw.transliterate(data['manufacturer'])
        sku = Sw.transliterate(data['herstellernummer'])
        data['image'] = cls.generate_img(sku, f'{brand}_{sku}', f'{path}')
        data['small_image'] = data['image']
        data['thumbnail'] = data['image']
        data['media_gallery'] = data['image']
        data['logo'] = 'x'

    @staticmethod
    def generate_img(sku, name, path='images'):
        file_name = f'{Sw.good_name(name)}.jpg'
        full_path = f'{path}\\{file_name}'
        if os.path.exists(full_path): return file_name
        print(f'generate img  {full_path}')
        fnt = ImageFont.truetype('C:\Windows\Fonts\Arial.ttf', 60)
        img = Image.open('logo.png').convert('RGB')
        d = ImageDraw.Draw(img)
        d.text((60, 880), sku, fill=0, font=fnt)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        img.save(full_path, quality=100, optimize=True, progressive=True)
        return file_name

    @staticmethod
    def delete_file(url):
        file_name = Sw.get_cache_path(url)
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f'=== delete file  {url}')
        else:
            print(f'=== file not found  {url}')

    @classmethod
    def driver_quit(cls):
        if cls._driver: cls._driver.quit()

    @classmethod
    def start_stop_decorator(cls, debug=False):
        def wrapper1(func):
            def wrapper2(*args, **kwargs):
                start_time = time.time()
                SwPrint(debug=debug)
                result = func(*args, **kwargs)
                print(f'done in {generate_time_string(time.time() - start_time)}')
                print(f'end')
                cls.driver_quit()
                SwPrint.save_log_to_file()
                return result

            return wrapper2

        return wrapper1

    @classmethod
    def unwrap_links(cls, soup):
        for tag in soup.find_all('a'):
            href = tag.get('href', '')
            # print(f'link unwrapped  {href}')
            tag.unwrap()

    @classmethod
    def get_images(cls, soup, source_url='', target_url=''):
        for tag in soup.find_all('img'):
            src = urljoin(source_url, tag.get('src', ''))
            print(f'got image  {src}')
            filename = cls.get_file_from_web(src, name='', path='imgs')
            tag.attrs.clear()
            tag.attrs['src'] = f'{target_url}{filename}'

    @classmethod
    def correct_images_sources(cls, soup, source_url=''):
        for tag in soup.find_all('img'):
            src = urljoin(source_url, tag.get('src'))
            print(f'got image  {src}')
            tag.attrs.clear()
            tag.attrs['src'] = src
