import Product


class Category:
    categories = {}

    def __init__(self, name, parent, en_name=None, entity_id=''):
        if not (name and isinstance(name, str)): raise ValueError('Category_init')
        self.name = name
        if not (parent is None or isinstance(parent, Category)): raise ValueError('Category_init')
        self.parent = parent
        if parent: self.parent.children.add(self)
        self.entity_id = entity_id
        self.children = set()
        self.categories[str(self)] = self
        self.position = '1'
        self.is_anchor = '1'
        if not (en_name is None or isinstance(en_name, str)): raise ValueError('Category_init')
        self.en_name = en_name or ''
        self.id = None

    def __str__(self):
        path = self.path()
        return f'{path}|{self.name}' if path else f'{self.name}'

    def __repr__(self):
        path = self.path()
        return f'{path}|{self.name}' if path else f'{self.name}'

    def path(self, cats=None):
        if cats is None: cats = []
        if not isinstance(cats, list): raise ValueError('Category_path')
        if self.parent:
            cats.append(self.parent.name)
            return self.parent.path(cats)
        else:
            return '|'.join(cats[::-1])

    def find_children(self, show_cats=True, show_products=True, text=False):
        if not isinstance(show_cats, bool): raise ValueError('Category_children')
        if not isinstance(show_products, bool): raise ValueError('Category_children')
        if not isinstance(text, bool): raise ValueError('Category_children')
        if not text:
            result = []
            if show_cats:
                children_categories = [cat for cat in self.children if isinstance(cat, Category)]
                result.extend(children_categories)
            if show_products:
                children_products = [product for product in self.children if isinstance(product, Product.Product)]
                result.extend(children_products)
            return result
        else:
            result = ''
            if show_cats:
                children_categories = [cat.name for cat in self.children if isinstance(cat, Category)]
                if children_categories:
                    result += f'Categories({len(children_categories)}): ' + ', '.join(children_categories) + '\n'
            if show_products:
                children_products = [product.full_sku for product in self.children if
                                     isinstance(product, Product.Product)]
                if children_products:
                    result += f'Products({len(children_products)}): ' + ', '.join(children_products)
            return result.strip('\n')

    @property
    def children_categories_count(self):
        return len([cat for cat in self.children if isinstance(cat, Category)])

    @property
    def children_products_count(self):
        return len([product for product in self.children if isinstance(product, Product.Product)])

    def add_product(self, product):
        if not isinstance(product, Product.Product): raise ValueError('bad add_product')
        self.children.add(product)
        product.categories.add(self)

    @classmethod
    def create_category(cls, path, en_path=None, entity_id=''):
        if not isinstance(path, str): raise ValueError('Category_create_category')
        if not (en_path is None or isinstance(path, str)): raise ValueError('Category_create_category')
        path = path.split('|')
        if en_path:
            en_path = en_path.split('|')
            if len(path) != len(en_path):
                print('=== разная длина пути категорий  {path}  {en_path}')
                en_path = None
        for i in range(len(path)):
            check_path = '|'.join(path[0:i + 1])
            find_result = cls.categories.get(check_path, None)
            if not find_result:
                parent_path = '|'.join(path[0:i])
                find_result = Category(
                    path[i],
                    cls.categories.get(parent_path, None),
                    en_path[i] if en_path else None,
                    entity_id if (i == len(path) - 1) else ''
                )
        return find_result

    def export(self):
        data = {}
        data['entity_id'] = self.entity_id
        data['path'] = self.path()
        data['name'] = self.name
        data['position'] = self.position
        data['is_anchor'] = self.is_anchor
        data['en_name'] = self.en_name
        return data

    @classmethod
    def count(cls):
        return len(cls.categories)

    def delete(self):
        self.categories.pop(str(self))
        if self.parent:
            self.parent.children.remove(self)
            for child in self.children:
                if isinstance(child, Category):
                    child.parent = self.parent
                if isinstance(child, Product.Product):
                    child.categories.remove(self)
                    child.categories.add(self.parent)
                self.parent.children.add(child)
        else:
            raise ValueError
        Category.reindex()
        # print(f'категория {str(self)} удалена')

    @classmethod
    def reindex(cls):
        cls.categories = {str(cat): cat for cat in cls.categories.values()}

    @classmethod
    def clear(cls):
        cls.categories = {}

    @classmethod
    def reorganize_categories(cls, lang, col=1):
        new_cat_name = {'de': 'Mehr', 'en': 'More', 'ru': 'Разное'}
        print(f'всего {int(cls.count() / col)} категорий')
        while True:
            a, b = 0, 0
            for each in list(cls.categories.values()).copy():
                if str(each).count('|') < 3: continue
                ### удаляем папки с количеством товаров меньше 3
                if each.children_categories_count == 0 and each.children_products_count < 3:
                    each.delete()
                    a += 1
                ### удаляем промежуточные папки без товаров
                elif each.children_categories_count == 1 and each.children_products_count == 0:
                    each.delete()
                    b += 1
            if a or b: print(f'удалено {int(a / col)}+{int(b / col)} категорий')
            if (a + b) == 0: break
        print(f'всего {int(cls.count() / col)} категорий')

        ### перемещаем "промежуточные" товары в новую папку
        while True:
            c = 0
            for each in list(cls.categories.values()).copy():
                if each.children_categories_count > 0 and each.children_products_count > 0:
                    new_cat = cls.create_category(f'{each}|{new_cat_name[lang]}')
                    for child in each.find_children(show_cats=False, show_products=True, text=False):
                        child.move(each, new_cat)
                    c += 1
            if c: print(f'создано {c // col} новых категорий {new_cat_name[lang]}. '
                        f'итого {cls.count() // col} категорий')
            if c == 0: break

    @classmethod
    def find_english_names(cls, site_categories, products):
        import LoadDictFromFile
        for each in site_categories.values():
            full_path = f"{each['path']}|{each['name']}"
            full_path_en = LoadDictFromFile.LoadDictFromFile.find_value(products, 'category_ids', full_path)
            if not full_path_en: continue
            cls.create_category(
                full_path,
                en_path=full_path_en.get('category_ids_en', ''),
                entity_id=each['entity_id'])
        for each in site_categories.values():
            find_result = cls.categories.get(f"{each['path']}|{each['name']}", None)
            if find_result: each['new_name'] = find_result.en_name
