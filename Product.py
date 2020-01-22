import Category


class Product:
    products = {}

    def __init__(self, full_sku):
        if not (full_sku and isinstance(full_sku, str)): raise ValueError('Product_init')
        if full_sku in self.products: raise ValueError('Product exist')
        self.full_sku = full_sku
        self.categories = set()
        self.products[full_sku] = self

    def __str__(self):
        return f'{self.full_sku}'

    @classmethod
    def count(cls):
        return len(cls.products)

    def export(self):
        data = {}
        data['full_sku'] = self.full_sku
        data['category_ids'] = '||'.join([str(each) for each in self.categories])
        return data

    @classmethod
    def export_categories(cls, full_sku):
        if not (full_sku and isinstance(full_sku, str)): raise ValueError
        return '||'.join([str(each) for each in cls.products[full_sku].categories])

    def move(self, old_cat, new_cat):
        if not (old_cat and isinstance(old_cat, Category.Category)): raise ValueError
        if not (new_cat and isinstance(new_cat, Category.Category)): raise ValueError
        self.categories.remove(old_cat)
        self.categories.add(new_cat)
        old_cat.children.remove(self)
        new_cat.children.add(self)
        return True

    def add_categories(self, paths):
        for path in paths.split('||'):
            cat = Category.Category.categories.get(path, None)
            if cat:
                cat.children.add(self)
                self.categories.add(cat)
            else:
                raise ValueError

    @classmethod
    def create_product(cls, full_sku, paths=None):
        if full_sku not in cls.products:
            new = Product(full_sku)
            if paths: new.add_categories(paths)
            return new
        else:
            exist = cls.products[full_sku]
            if paths: exist.add_categories(paths)
            return exist

    @classmethod
    def clear(cls):
        cls.products = {}
