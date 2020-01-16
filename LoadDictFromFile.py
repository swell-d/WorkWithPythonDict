import codecs
import csv
import os
import re
import unittest
from datetime import datetime

from openpyxl import load_workbook
from xlrd import open_workbook

from CheckTypes import CheckTypesRe as CheckTypes
from GlobalFunctions import print, print_run_time


class LoadDictFromFile:
    __optimize, __recognize = None, None

    @classmethod
    def __correct(cls, value, for_xls=False):
        if value is None: return ''
        if cls.__optimize and isinstance(value, str): return re.sub(r'\s+', ' ', value).strip()
        if cls.__recognize:
            return value
        else:
            if for_xls and isinstance(value, float) and str(value).endswith('.0'): return str(value)[:-2]
            return str(value)

    @classmethod
    def __titles(cls, titles_original, language):
        titles = []
        for each in titles_original:
            new_name1 = each[each.find('<') + 1:each.find('>')] if ('<' in each and '>' in each) else each
            new_name2 = each[each.find('(') + 1:each.find(')')] if ('(' in each and ')' in each) else ''
            if new_name2 == language: new_name1 += '_' + new_name2
            titles.append(cls.__correct(new_name1))
        return titles

    @staticmethod
    def __find_index(maincolumn, titles):
        if maincolumn is None and 'sku' in titles:
            return titles.index('sku')
        elif maincolumn in titles:
            return titles.index(maincolumn)
        return None

    @classmethod
    def __xls_titles(cls, sheet):
        titles_original = []
        for column in range(0, sheet.ncols):
            data = str(cls.__correct(sheet.cell(0, column).value, for_xls=True))
            if data == '': break
            titles_original.append(data)
        return titles_original

    @classmethod
    def __xlsx_titles(cls, sheet):
        titles_original = []
        for column in range(1, sheet.max_column + 1):
            data = str(cls.__correct(sheet.cell(row=1, column=column).value))
            if data == '': break
            titles_original.append(data)
        return titles_original

    @classmethod
    @print_run_time
    def _csv_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter, quotechar='"')
            data = [row for row in reader]
        titles = cls.__titles(data[0], language)
        index = cls.__find_index(maincolumn, titles)
        check_types = CheckTypes()
        for row in data[1:]:
            if not len(row): continue
            name = str(cls.__correct(row[index]) if index is not None else len(imports) + 1)
            if name: imports[name] = {
                titles[i]: check_types.return_int_str(cls.__correct(row[i])) if recognize else cls.__correct(row[i])
                for i in range(0, len(titles))}
        print(f"{filename} / {len(data) - 1} lines / {len(imports)} loaded / {len(data) - 1 - len(imports)} lost / ",
              end='')
        return imports

    @classmethod
    @print_run_time
    def _xls_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        sheet = open_workbook(filename).sheet_by_index(0)
        titles = cls.__titles(cls.__xls_titles(sheet), language)
        index = cls.__find_index(maincolumn, titles)
        for a in range(1, sheet.nrows):
            row = [cls.__correct(sheet.cell(a, col).value, for_xls=True) for col in range(0, len(titles))]
            name = str(row[index] if index is not None else len(imports) + 1)
            if name: imports[name] = {titles[i]: row[i] for i in range(0, len(titles))}
        print(
            f"{filename} / {sheet.nrows - 1} lines / {len(imports)} loaded / {sheet.nrows - 1 - len(imports)} lost / ",
            end='')
        return imports

    @classmethod
    @print_run_time
    def _xlsx_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        sheet = load_workbook(filename).active
        titles = cls.__titles(cls.__xlsx_titles(sheet), language)
        index = cls.__find_index(maincolumn, titles)
        for a in range(2, sheet.max_row + 1):
            row = [cls.__correct(sheet.cell(row=a, column=col).value) for col in range(1, len(titles) + 1)]
            name = str(row[index] if index is not None else len(imports) + 1)
            if name: imports[name] = {titles[i]: row[i] for i in range(0, len(titles))}
        print(
            f"{filename} / {sheet.max_row - 1} lines / {len(imports)} loaded / {sheet.max_row - 1 - len(imports)} lost / ",
            end='')
        return imports

    @classmethod
    def load(cls, filename, maincolumn=None, language=None, optimize=False, recognize=False, delimiter=','):
        if filename.endswith('.csv'):
            func = cls._csv_import
        elif filename.endswith('.xls'):
            func = cls._xls_import
        elif filename.endswith('.xlsx') or filename.endswith('.xlsm'):
            func = cls._xlsx_import
        else:
            raise ValueError('Wrong filetype')
        return func(filename, maincolumn, language, optimize, recognize, delimiter)

    @staticmethod
    def change_main_column(data, maincolumn):
        result = {}
        for each in data.values(): result[each[maincolumn]] = each
        print(f'change_main_column: {len(data)} lines / {len(result)} loaded / {len(data) - len(result)} lost')
        return result

    @staticmethod
    def count_not_empty_values(data, column):
        result = 0
        for each in data.values():
            value = each.get(column, None)
            if value is not None and value != '':
                result += 1
        return result

    @staticmethod
    def count_values(data, column, value):
        result = 0
        for each in data.values():
            if each.get(column, '') == value:
                result += 1
        return result


class LoadDictFromFileTests(unittest.TestCase):
    __DATE = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
    __data_xls = {'1.0': {'#': 1.0, 'first': '1\n1', 'second': 22.2, 'third': ''},
                  '2.0': {'#': 2.0, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_xls_not_recognized = {'1.0': {'#': '1.0', 'first': '1\n1', 'second': '22.2', 'third': ''},
                                 '2.0': {'#': '2.0', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_optimized_xls = {'1.0': {'#': 1.0, 'first': '1 1', 'second': 22.2, 'third': ''},
                            '2.0': {'#': 2.0, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
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
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.csv', maincolumn='#', recognize=True)
        self.assertEqual(self.__data_csv, test_dict)
        test_dict2 = LoadDictFromFile.load('files_for_tests/test_import.csv', maincolumn='#', optimize=True,
                                           recognize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict2)
        test_dict3 = LoadDictFromFile.load('files_for_tests/test_import.csv', recognize=True)
        self.assertEqual(self.__data_csv, test_dict3)
        test_dict4 = LoadDictFromFile.load('files_for_tests/test_import.csv', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_csv, test_dict4)

    def test_xls_import(self):
        test_dict1 = LoadDictFromFile.load('files_for_tests/test_import.xls', maincolumn='#', recognize=True)
        self.assertEqual(self.__data_xls, test_dict1)
        test_dict2 = LoadDictFromFile.load('files_for_tests/test_import.xls', maincolumn='#', optimize=True,
                                           recognize=True)
        self.assertEqual(self.__data_optimized_xls, test_dict2)
        # test_dict3 = LoadDictFromFile.load('test_import.xls', recognize=True)
        # self.assertEqual(self.__data_xls, test_dict3)
        # test_dict4 = LoadDictFromFile.load('test_import.xls', optimize=True, recognize=True)
        # self.assertEqual(self.__data_optimized_xls, test_dict4)
        test_dict5 = LoadDictFromFile.load('files_for_tests/test_import.xls', maincolumn='#', recognize=False)
        self.assertEqual(self.__data_xls_not_recognized, test_dict5)

    def test_xlsx_import(self):
        test_dict1 = LoadDictFromFile.load('files_for_tests/test_import.xlsx', maincolumn='#', recognize=True)
        self.assertEqual(self.__data_xlsx, test_dict1)
        test_dict2 = LoadDictFromFile.load('files_for_tests/test_import.xlsx', maincolumn='#', optimize=True,
                                           recognize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict2)
        test_dict3 = LoadDictFromFile.load('files_for_tests/test_import.xlsx', recognize=True)
        self.assertEqual(self.__data_xlsx, test_dict3)
        test_dict4 = LoadDictFromFile.load('files_for_tests/test_import.xlsx', optimize=True, recognize=True)
        self.assertEqual(self.__data_optimized_xlsx, test_dict4)
        test_dict5 = LoadDictFromFile.load('files_for_tests/test_import.xlsx', maincolumn='#', recognize=False)
        self.assertEqual(self.__data_xlsx_not_recognized, test_dict5)

    def test_csv_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_csv(self.__data_csv, filename='test')
        self.assertEqual(self.__data_csv,
                         LoadDictFromFile.load(f'{self.__DATE}_test.csv', recognize=True))
        self.assertEqual(self.__data_optimized_csv,
                         LoadDictFromFile.load(f'{self.__DATE}_test.csv', optimize=True, recognize=True))
        os.remove(f'{self.__DATE}_test.csv')

    def test_xlsx_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        SaveDictToFile.save_to_xlsx(self.__data_xlsx, filename='test')
        self.assertEqual(self.__data_xlsx,
                         LoadDictFromFile.load(f'{self.__DATE}_test.xlsx', recognize=True))
        self.assertEqual(self.__data_optimized_xlsx,
                         LoadDictFromFile.load(f'{self.__DATE}_test.xlsx', optimize=True, recognize=True))
        os.remove(f'{self.__DATE}_test.xlsx')


if __name__ == '__main__':
    unittest.main()
