import os
import pathlib
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

from TextCorrections import TextCorrections as sw
from parsing_classes import Category
from parsing_classes import Product


class Parsing:
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

        # same for all
        url_key = f"{data['manufacturer']}_{data['herstellernummer']}".strip('_').lower()
        url_key = url_key.replace('/', '-').replace('\\', '-').replace(' ', '-').replace('+', '-').replace('.', '-')
        data['url_key'] = quote(url_key)
        data['status'] = 1
        data['qty'] = 1000
        data['is_in_stock'] = 1
        data['tax_class_id'] = 'Vollbesteuerte Artikel' if lang != 'ru' else ''
        data['attribute_set_name'] = 'Default' if lang != 'ru' else ''

        # additional
        # data['special_price'] = ''
        # data['weight'] = ''
        # data['ean'] = ''
        # data['delivery_time'] = ''
        # data['relation'] = ''  # через ||

        return data
