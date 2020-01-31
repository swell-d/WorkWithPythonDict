import codecs
import csv
import os
import re
import unittest

import openpyxl
import xlrd

import CheckTypes
import GlobalFunctions
from GlobalFunctions import print


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
        last_not_empty_column = 0
        for column in range(0, sheet.ncols):
            data = str(cls.__correct(sheet.cell(0, column).value, for_xls=True))
            if data == '':
                data = openpyxl.utils.get_column_letter(column + 1)
            else:
                last_not_empty_column = column + 1
            titles_original.append(data)
        return titles_original[:last_not_empty_column]

    @classmethod
    def __xlsx_titles(cls, sheet):
        titles_original = []
        last_not_empty_column = 0
        for column in range(1, sheet.max_column + 1):
            data = str(cls.__correct(sheet.cell(row=1, column=column).value))
            if data == '':
                data = openpyxl.utils.get_column_letter(column)
            else:
                last_not_empty_column = column
            titles_original.append(data)
        return titles_original[:last_not_empty_column]

    @classmethod
    @GlobalFunctions.print_run_time
    def _csv_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        with codecs.open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter, quotechar='"')
            data = [row for row in reader]
        titles = cls.__titles(data[0], language)
        index = cls.__find_index(maincolumn, titles)
        if recognize: check_types = CheckTypes.CheckTypesRe()
        for a, row in enumerate(data[1:]):
            if not len(row): continue
            name = str(cls.__correct(row[index]) if index is not None else a + 2)
            if name: imports[name] = {
                titles[i]: check_types.return_int_or_str(cls.__correct(row[i])) if recognize else cls.__correct(row[i])
                for i in range(0, len(titles))}
        print(f"{filename} / {len(data) - 1} lines / {len(imports)} loaded / {len(data) - 1 - len(imports)} lost / ",
              end='')
        return imports

    @classmethod
    @GlobalFunctions.print_run_time
    def _xls_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        sheet = xlrd.open_workbook(filename).sheet_by_index(0)
        titles = cls.__titles(cls.__xls_titles(sheet), language)
        index = cls.__find_index(maincolumn, titles)
        for a in range(1, sheet.nrows):
            row = [cls.__correct(sheet.cell(a, col).value, for_xls=True) for col in range(0, len(titles))]
            name = str(row[index] if index is not None else a + 1)
            if name: imports[name] = {titles[i]: row[i] for i in range(0, len(titles))}
        print(
            f"{filename} / {sheet.nrows - 1} lines / {len(imports)} loaded / {sheet.nrows - 1 - len(imports)} lost / ",
            end='')
        return imports

    @classmethod
    @GlobalFunctions.print_run_time
    def _xlsx_import(cls, filename, maincolumn, language, optimize, recognize, delimiter):
        cls.__optimize, cls.__recognize = optimize, recognize
        imports = {}
        sheet = openpyxl.load_workbook(filename).active
        titles = cls.__titles(cls.__xlsx_titles(sheet), language)
        index = cls.__find_index(maincolumn, titles)
        for a in range(2, sheet.max_row + 1):
            row = [cls.__correct(sheet.cell(row=a, column=col).value) for col in range(1, len(titles) + 1)]
            name = str(row[index] if index is not None else a)
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

    @staticmethod
    def find_value(data, key, value):
        for each in data.values():
            found_value = each.get(key, '')
            if found_value == value: return each


class LoadDictFromFileTests(unittest.TestCase):
    # CSV
    __csv = {'2': {'#': '1', 'first': '1\r\n1', 'second': '22,2', 'third': ''},
             '3': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __csv_main = {'1': {'#': '1', 'first': '1\r\n1', 'second': '22,2', 'third': ''},
                  '2': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __csv_recogn = {'2': {'#': 1, 'first': '1\r\n1', 'second': '22,2', 'third': ''},
                    '3': {'#': 2, 'first': '', 'second': 12345678901234567890, 'third': '"4""4'}}  # Todo float
    __csv_optim = {'2': {'#': '1', 'first': '1 1', 'second': '22,2', 'third': ''},
                   '3': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    # XLS
    __xls = {'2': {'#': '1', 'first': '1\n1', 'second': '22.2', 'third': ''},
             '3': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __xls_main = {'1': {'#': '1', 'first': '1\n1', 'second': '22.2', 'third': ''},
                  '2': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __xls_recogn = {'2': {'#': 1, 'first': '1\n1', 'second': 22.2, 'third': ''},
                    '3': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}  # Todo int+float
    __xls_optim = {'2': {'#': '1', 'first': '1 1', 'second': '22.2', 'third': ''},
                   '3': {'#': '2', 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}

    def test_csv_import(self):
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.csv')
        self.assertEqual(self.__csv, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.csv', maincolumn='#')
        self.assertEqual(self.__csv_main, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.csv', recognize=True)
        self.assertEqual(self.__csv_recogn, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.csv', optimize=True)
        self.assertEqual(self.__csv_optim, test_dict)

    def test_xls_import(self):
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xls')
        self.assertEqual(self.__xls, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xls', maincolumn='#')
        self.assertEqual(self.__xls_main, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xls', recognize=True)
        self.assertEqual(self.__xls_recogn, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xls', optimize=True)
        self.assertEqual(self.__xls_optim, test_dict)

    def test_xlsx_import(self):
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xlsx')
        self.assertEqual(self.__xls, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xlsx', maincolumn='#')
        self.assertEqual(self.__xls_main, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xlsx', recognize=True)
        self.assertEqual(self.__xls_recogn, test_dict)
        test_dict = LoadDictFromFile.load('files_for_tests/test_import.xlsx', optimize=True)
        self.assertEqual(self.__xls_optim, test_dict)

    def test_csv_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        tmp = SaveDictToFile.save_to_csv(self.__csv)
        self.assertEqual(self.__csv, LoadDictFromFile.load(tmp))
        self.assertEqual(self.__csv_main, LoadDictFromFile.load(tmp, maincolumn='#'))
        self.assertEqual(self.__csv_recogn, LoadDictFromFile.load(tmp, recognize=True))
        self.assertEqual(self.__csv_optim, LoadDictFromFile.load(tmp, optimize=True))
        os.remove(tmp)

    def test_xlsx_in_and_out(self):
        from SaveDictToFile import SaveDictToFile
        tmp = SaveDictToFile.save_to_xlsx(self.__xls)
        self.assertEqual(self.__xls, LoadDictFromFile.load(tmp))
        self.assertEqual(self.__xls_main, LoadDictFromFile.load(tmp, maincolumn='#'))
        # self.assertEqual(self.__xls_recogn, LoadDictFromFile.load(tmp, recognize=True))  # Todo int+float
        self.assertEqual(self.__xls_optim, LoadDictFromFile.load(tmp, optimize=True))
        os.remove(tmp)


if __name__ == '__main__':
    unittest.main()
