import os
import pathlib

from PIL import Image, ImageDraw, ImageFont

from TextCorrections import TextCorrections as sw


class Parsing:
    @staticmethod
    def check_sku(sku, url, good_symbols='.-'):
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
        if not data.get('image'):
            data['image'] = cls.generate_img(f'{sku}', f'{brand}_{sku}', path).replace('png', 'jpg')
            data['small_image'] = data['image']
            data['thumbnail'] = data['image']
            data['media_gallery'] = data['image']
        return data

    @staticmethod
    def generate_img(sku, name, path='images'):
        name = sw.good_name(name)
        short_file_name = os.path.join(path, name).lower()
        file_type = '.jpg'
        file_name = short_file_name + file_type
        if not os.path.exists(file_name):
            print(f'generate img  {sku}')
            fnt = ImageFont.truetype('C:\Windows\Fonts\Arial.ttf', 60)
            img = Image.open('logo.png')
            d = ImageDraw.Draw(img)
            d.text((60, 880), sku, fill=0, font=fnt)
            img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            img.save(file_name, colors=255)
        return (name + file_type).lower()
