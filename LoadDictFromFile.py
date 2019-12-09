import codecs
import csv
import os
import re
import unittest
from datetime import datetime

from openpyxl import load_workbook

import CheckTypes
from SaveDictToFile import print_run_time


class LoadDictFromFile:
    __SEPARATOR = ','
    __QUOTECHAR = '"'

    @classmethod
    def correct(cls, value):
        if value is None: return ''
        if cls.optimize and isinstance(value, str): return re.sub(r'\s+', ' ', value).strip()
        return value if cls.recognize else str(value)

    @classmethod
    def titles(cls, titles_original, language):
        titles = []
        for each in titles_original:
            new_name1 = each[each.find('<')+1:each.find('>')] if ('<' in each and '>' in each) else each
            new_name2 = each[each.find('(')+1:each.find(')')] if ('(' in each and ')' in each) else ''
            if new_name2 == language: new_name1 += '_' + new_name2
            titles.append(cls.correct(new_name1))
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
            data = str(cls.correct(sheet.cell(row=1, column=column).value))
            if data == '': break
            titles_original.append(data)
        return titles_original

    @classmethod
    @print_run_time
    def csv_import(cls, filename, maincolumn=None, language=None, optimize=False, recognize=False):
        cls.optimize, cls.recognize = optimize, recognize
        imports = {}
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=cls.__SEPARATOR, quotechar=cls.__QUOTECHAR)
            data = [row for row in reader]
        titles = cls.titles(data[0], language)
        index = cls.find_index(maincolumn, titles)
        check_types = CheckTypes.CheckTypesRe()
        for row in data[1:]:
            name = str(cls.correct(row[index]) if index is not None else len(imports) + 1)
            if name: imports[name] = {titles[i]: check_types.return_int_str(cls.correct(row[i])) if recognize else cls.correct(row[i])
                                      for i in range(0, len(titles))}
        return imports

    @classmethod
    @print_run_time
    def xlsx_import(cls, filename, maincolumn=None, language=None, optimize=False, recognize=False):
        cls.optimize, cls.recognize = optimize, recognize
        imports = {}
        sheet = load_workbook(filename).active
        titles = cls.titles(cls.titles_original(sheet), language)
        index = cls.find_index(maincolumn, titles)
        for a in range(2, sheet.max_row+1):
            row = [cls.correct(sheet.cell(row=a, column=col).value) for col in range(1, len(titles)+1)]
            name = str(row[index] if index is not None else len(imports) + 1)
            if name: imports[name] = {titles[i]: row[i]
                                      for i in range(0, len(titles))}
        return imports


class LoadDictFromFileTests(unittest.TestCase):
    __DATE = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
    __data_xlsx = {'1': {'#': 1, 'first': '1\n1', 'second': 22.2, 'third': ''},
                   '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_xlsx_not_recognized = {'1': {'#': '1', 'first': '1\n1', 'second': '22.2', 'third': ''},
                                  '2': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_optimized_xlsx = {'1': {'#': 1, 'first': '1 1', 'second': 22.2, 'third': ''},
                             '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_csv = {'1': {'#': 1, 'first': '1\r\n1', 'second': '22,2', 'third': ''},  # Todo recognize float
                  '2': {'#': 2, 'first': '', 'second': 12345678901234567890, 'third': '"4""4'}}
    __data_optimized_csv = {'1': {'#': 1, 'first': '1 1', 'second': '22,2', 'third': ''},  # Todo recognize float
                            '2': {'#': 2, 'first': '', 'second': 12345678901234567890, 'third': '"4""4'}}

    def test_csv_import(self):
        test_dict = LoadDictFromFile.csv_import('test_import.csv', maincolumn='#', recognize=True)
        self.assertEqual(self.__data_csv, test_dict)
        test_dict2 = LoadDictFromFile.csv_import('test_import.csv', maincolumn='#', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict2)
        test_dict3 = LoadDictFromFile.csv_import('test_import.csv', recognize=True)
        self.assertEqual(self.__data_csv, test_dict3)
        test_dict4 = LoadDictFromFile.csv_import('test_import.csv', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict4)

    def test_xlsx_import(self):
        test_dict1 = LoadDictFromFile.xlsx_import('test_import.xlsx', maincolumn='#', recognize=True)
        self.assertEqual(self.__data_xlsx, test_dict1)
        test_dict2 = LoadDictFromFile.xlsx_import('test_import.xlsx', maincolumn='#', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict2)
        test_dict3 = LoadDictFromFile.xlsx_import('test_import.xlsx', recognize=True)
        self.assertEqual(self.__data_xlsx, test_dict3)
        test_dict4 = LoadDictFromFile.xlsx_import('test_import.xlsx', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict4)
        test_dict5 = LoadDictFromFile.xlsx_import('test_import.xlsx', maincolumn='#', recognize=False)
        self.assertEqual(self.__data_xlsx_not_recognized, test_dict5)

    def test_csv_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_csv(self.__data_csv, filename='test')
        self.assertEqual(self.__data_csv,
                         LoadDictFromFile.csv_import(f'{self.__DATE}_test.csv', recognize=True))
        self.assertEqual(self.__data_optimized_csv,
                         LoadDictFromFile.csv_import(f'{self.__DATE}_test.csv', optimize=True, recognize=True))
        os.remove(f'{self.__DATE}_test.csv')

    def test_xlsx_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_xlsx(self.__data_xlsx, filename='test')
        self.assertEqual(self.__data_xlsx,
                         LoadDictFromFile.xlsx_import(f'{self.__DATE}_test.xlsx', recognize=True))
        self.assertEqual(self.__data_optimized_xlsx,
                         LoadDictFromFile.xlsx_import(f'{self.__DATE}_test.xlsx', optimize=True, recognize=True))
        os.remove(f'{self.__DATE}_test.xlsx')


if __name__ == '__main__':
    unittest.main()
