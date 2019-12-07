import codecs
import csv
import os
import re
import unittest
from datetime import datetime
from openpyxl import load_workbook
from SaveDictToFile import print_run_time


class LoadDictFromFile():
    __SEPARATOR = ','
    __QUOTECHAR = '"'
    int_compile = re.compile(r"^-?[1-9]\d*$")
    float_compile = re.compile(r"^0$|^-?0[.,]\d+$|^-?[1-9]\d*([.,]\d+)?$")

    @classmethod
    def isint(cls, text):
        if len(text) > 10: return False
        return True if re.match(cls.int_compile, text) else False

    @classmethod
    def isfloat(cls, text):
        if len(text) > 10: return False
        return True if re.match(cls.float_compile, text) else False

    @classmethod
    def clr(cls, value):
        if isinstance(value, str): return re.sub(r'\s+', ' ', value).strip()
        return value if value is not None else ''

    @staticmethod
    def none_to_empty(value):
        return value if value is not None else ''

    @classmethod
    def titles(cls, titles_original, language, correct):
        titles = []
        for each in titles_original:
            new_name1 = each[each.find('<')+1:each.find('>')] if ('<' in each and '>' in each) else each
            new_name2 = each[each.find('(')+1:each.find(')')] if ('(' in each and ')' in each) else ''
            if new_name2 == language: new_name1 += '_' + new_name2
            titles.append(correct(new_name1))
        return titles

    @staticmethod
    def find_index(maincolumn, titles):
        if maincolumn is None and 'sku' in titles: return titles.index('sku')
        elif maincolumn in titles: return titles.index(maincolumn)
        return None

    @classmethod
    def titles_original(cls, sheet):
        titles_original = []
        for column in range(1, sheet.max_column + 1):
            data = str(cls.none_to_empty(sheet.cell(row=1, column=column).value))
            if data == '': break
            titles_original.append(data)
        return titles_original

    @classmethod
    @print_run_time
    def csv_import(cls, filename, maincolumn=None, language=None, optimize=False):
        imports = {}
        correct = cls.none_to_empty if not optimize else cls.clr
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=cls.__SEPARATOR, quotechar=cls.__QUOTECHAR)
            data = [row for row in reader]
        titles = cls.titles(data[0], language, correct)
        index = cls.find_index(maincolumn, titles)
        for row in data[1:]:
            name = str(correct(row[index] if index is not None else len(imports) + 1))
            if name: imports[name] = {titles[i]: cls.return_int_float_str(correct(row[i])) for i in range(0, len(titles))}
        return imports

    @classmethod
    def return_int_float_str(cls, text):
        if cls.isint(text): return int(text)
        # if cls.isfloat(text): return float(text.replace(',', '.'))  # Todo recognize float
        return text

    @classmethod
    @print_run_time
    def xlsx_import(cls, filename, maincolumn=None, language=None, optimize=False):
        imports = {}
        correct = cls.none_to_empty if not optimize else cls.clr
        sheet = load_workbook(filename).active
        titles = cls.titles(cls.titles_original(sheet), language, correct)
        index = cls.find_index(maincolumn, titles)
        for a in range(2, sheet.max_row+1):
            row = [sheet.cell(row=a, column=col).value for col in range(1, len(titles)+1)]
            name = str(correct(row[index] if index is not None else len(imports) + 1))
            if name: imports[name] = {titles[i]: correct(row[i]) for i in range(0, len(titles))}
        return imports


class LoadDictFromFileTests(unittest.TestCase):
    __DATE = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
    __data_xlsx = {'1': {'#': 1, 'first': '1\n1', 'second': 22.2, 'third': ''},
                   '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_optimized_xlsx = {'1': {'#': 1, 'first': '1 1', 'second': 22.2, 'third': ''},
                             '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_csv = {'1': {'#': 1, 'first': '1\r\n1', 'second': '22,2', 'third': ''},  # Todo recognize float
                  '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_optimized_csv = {'1': {'#': 1, 'first': '1 1', 'second': '22,2', 'third': ''},  # Todo recognize float
                            '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}

    def test_csv_import(self):
        test_dict = LoadDictFromFile.csv_import('test_import.csv', maincolumn='#')
        self.assertEqual(self.__data_csv, test_dict)
        test_dict2 = LoadDictFromFile.csv_import('test_import.csv', maincolumn='#', optimize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict2)
        test_dict3 = LoadDictFromFile.csv_import('test_import.csv')
        self.assertEqual(self.__data_csv, test_dict3)
        test_dict4 = LoadDictFromFile.csv_import('test_import.csv', optimize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict4)

    def test_xlsx_import(self):
        test_dict = LoadDictFromFile.xlsx_import('test_import.xlsx', maincolumn='#')
        self.assertEqual(self.__data_xlsx, test_dict)
        test_dict2 = LoadDictFromFile.xlsx_import('test_import.xlsx', maincolumn='#', optimize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict2)
        test_dict3 = LoadDictFromFile.xlsx_import('test_import.xlsx')
        self.assertEqual(self.__data_xlsx, test_dict3)
        test_dict4 = LoadDictFromFile.xlsx_import('test_import.xlsx', optimize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict4)

    def test_csv_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_csv(self.__data_csv, filename='test')
        self.assertEqual(self.__data_csv, LoadDictFromFile.csv_import(f'{self.__DATE}_test.csv'))
        self.assertEqual(self.__data_optimized_csv, LoadDictFromFile.csv_import(f'{self.__DATE}_test.csv', optimize=True))
        os.remove(f'{self.__DATE}_test.csv')

    def test_xlsx_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_xlsx(self.__data_xlsx, filename='test')
        self.assertEqual(self.__data_xlsx, LoadDictFromFile.xlsx_import(f'{self.__DATE}_test.xlsx'))
        self.assertEqual(self.__data_optimized_xlsx, LoadDictFromFile.xlsx_import(f'{self.__DATE}_test.xlsx', optimize=True))
        os.remove(f'{self.__DATE}_test.xlsx')

    def test_isfloat(self):
        good_values = ['-1', '0', '1', '-1.0', '1.0', '-0.1', '0.1', '911']
        bad_values = ['', ' ', '-', '+', '00', '01', '0123', '-0', '-00', '-01', '-0123',
                      '00.0', '01.', '-01.', '.1', '-.1', '1-', ' 1', '1 ', '-001',
                      '0.1.1', '1..1', '0..1']
        for val in good_values:
            self.assertTrue(LoadDictFromFile.isfloat(val), msg=val)
        for val in bad_values:
            self.assertFalse(LoadDictFromFile.isfloat(val), msg=val)


if __name__ == '__main__':
    unittest.main()
