import codecs
import csv
import os
import re
import unittest

import openpyxl
import xlrd

import CheckTypes
import GlobalFunctions
from GlobalFunctions import print  # Todo use logging


def __correct(value, optimize, recognize, for_xls=False):
    if value is None: return ''
    if optimize and isinstance(value, str): return re.sub(r'\s+', ' ', value).strip()
    if recognize:
        return value
    else:
        if for_xls and isinstance(value, float) and str(value).endswith('.0'): return str(value)[:-2]
        return str(value)


def __titles(titles_original, language, optimize, recognize):
    titles = []
    for each in titles_original:
        new_name1 = each[each.find('<') + 1:each.find('>')] if ('<' in each and '>' in each) else each
        new_name2 = each[each.find('(') + 1:each.find(')')] if ('(' in each and ')' in each) else ''
        if new_name2 == language: new_name1 += '_' + new_name2
        titles.append(__correct(new_name1, optimize, recognize))
    return titles


def __find_index(maincolumn, titles):
    if maincolumn is None and 'sku' in titles:
        return titles.index('sku')
    elif maincolumn in titles:
        return titles.index(maincolumn)
    return None


def __xls_titles(sheet, optimize, recognize):
    titles_original = []
    last_not_empty_column = 0
    for column in range(0, sheet.ncols):
        data = str(__correct(sheet.cell(0, column).value, optimize, recognize, for_xls=True))
        if data == '':
            data = openpyxl.utils.get_column_letter(column + 1)
        else:
            last_not_empty_column = column + 1
        titles_original.append(data)
    return titles_original[:last_not_empty_column]


def __xlsx_titles(sheet, optimize, recognize):
    titles_original = []
    last_not_empty_column = 0
    for column in range(1, sheet.max_column + 1):
        data = str(__correct(sheet.cell(row=1, column=column).value, optimize, recognize))
        if data == '':
            data = openpyxl.utils.get_column_letter(column)
        else:
            last_not_empty_column = column
        titles_original.append(data)
    return titles_original[:last_not_empty_column]


@GlobalFunctions.print_run_time
def _csv_import(filename, maincolumn, language, optimize, recognize, delimiter):
    imports = {}
    with codecs.open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=delimiter, quotechar='"')
        data = [row for row in reader]
    titles = __titles(data[0], language, optimize, recognize)
    index = __find_index(maincolumn, titles)
    if recognize: check_types = CheckTypes.CheckTypesRe()
    for a, row in enumerate(data[1:]):
        if not len(row): continue
        name = str(__correct(row[index], optimize, recognize) if index is not None else a + 2)
        if name: imports[name] = {
            titles[i]: check_types.return_int_or_str(
                __correct(row[i], optimize, recognize)) if recognize else __correct(row[i], optimize, recognize)
            for i in range(0, len(titles))}
    print(f"{filename} / {len(data) - 1} lines / {len(imports)} loaded / {len(data) - 1 - len(imports)} lost / ",
          end='')
    return imports


@GlobalFunctions.print_run_time
def _xls_import(filename, maincolumn, language, optimize, recognize, delimiter):
    imports = {}
    sheet = xlrd.open_workbook(filename).sheet_by_index(0)
    titles = __titles(__xls_titles(sheet, optimize, recognize), language, optimize, recognize)
    index = __find_index(maincolumn, titles)
    for a in range(1, sheet.nrows):
        row = [__correct(sheet.cell(a, col).value, optimize, recognize, for_xls=True) for col in range(0, len(titles))]
        name = str(row[index] if index is not None else a + 1)
        if name: imports[name] = {titles[i]: row[i] for i in range(0, len(titles))}
    print(
        f"{filename} / {sheet.nrows - 1} lines / {len(imports)} loaded / {sheet.nrows - 1 - len(imports)} lost / ",
        end='')
    return imports


@GlobalFunctions.print_run_time
def _xlsx_import(filename, maincolumn, language, optimize, recognize, delimiter):
    imports = {}
    sheet = openpyxl.load_workbook(filename).active
    titles = __titles(__xlsx_titles(sheet, optimize, recognize), language, optimize, recognize)
    index = __find_index(maincolumn, titles)
    for a in range(2, sheet.max_row + 1):
        row = [__correct(sheet.cell(row=a, column=col).value, optimize, recognize) for col in range(1, len(titles) + 1)]
        name = str(row[index] if index is not None else a)
        if name: imports[name] = {titles[i]: row[i] for i in range(0, len(titles))}
    print(
        f"{filename} / {sheet.max_row - 1} lines / {len(imports)} loaded / {sheet.max_row - 1 - len(imports)} lost / ",
        end='')
    return imports


def load(filename, maincolumn=None, language=None, optimize=False, recognize=False, delimiter=','):
    if filename.endswith('.csv'):
        func = _csv_import
    elif filename.endswith('.xls'):
        func = _xls_import
    elif filename.endswith('.xlsx') or filename.endswith('.xlsm'):
        func = _xlsx_import
    else:
        raise ValueError(f'Wrong filetype: {filename}')
    return func(filename, maincolumn, language, optimize, recognize, delimiter)


def change_main_column(data, maincolumn):
    result = {}
    for each in data.values(): result[each[maincolumn]] = each
    print(f'change_main_column: {len(data)} lines / {len(result)} loaded / {len(data) - len(result)} lost')
    return result


def count_not_empty_values(data, column):
    result = 0
    for each in data.values():
        value = each.get(column, None)
        if value is not None and value != '':
            result += 1
    return result


def count_values(data, column, value):
    result = 0
    for each in data.values():
        if each.get(column, '') == value:
            result += 1
    return result


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
        test_dict = load('files_for_tests/test_import.csv')
        self.assertEqual(self.__csv, test_dict)
        test_dict = load('files_for_tests/test_import.csv', maincolumn='#')
        self.assertEqual(self.__csv_main, test_dict)
        test_dict = load('files_for_tests/test_import.csv', recognize=True)
        self.assertEqual(self.__csv_recogn, test_dict)
        test_dict = load('files_for_tests/test_import.csv', optimize=True)
        self.assertEqual(self.__csv_optim, test_dict)

    def test_xls_import(self):
        test_dict = load('files_for_tests/test_import.xls')
        self.assertEqual(self.__xls, test_dict)
        test_dict = load('files_for_tests/test_import.xls', maincolumn='#')
        self.assertEqual(self.__xls_main, test_dict)
        test_dict = load('files_for_tests/test_import.xls', recognize=True)
        self.assertEqual(self.__xls_recogn, test_dict)
        test_dict = load('files_for_tests/test_import.xls', optimize=True)
        self.assertEqual(self.__xls_optim, test_dict)

    def test_xlsx_import(self):
        test_dict = load('files_for_tests/test_import.xlsx')
        self.assertEqual(self.__xls, test_dict)
        test_dict = load('files_for_tests/test_import.xlsx', maincolumn='#')
        self.assertEqual(self.__xls_main, test_dict)
        test_dict = load('files_for_tests/test_import.xlsx', recognize=True)
        self.assertEqual(self.__xls_recogn, test_dict)
        test_dict = load('files_for_tests/test_import.xlsx', optimize=True)
        self.assertEqual(self.__xls_optim, test_dict)

    def test_csv_in_and_out(self):
        import SaveDictToFile
        tmp = SaveDictToFile.save_to_csv(self.__csv)
        self.assertEqual(self.__csv, load(tmp))
        self.assertEqual(self.__csv_main, load(tmp, maincolumn='#'))
        self.assertEqual(self.__csv_recogn, load(tmp, recognize=True))
        self.assertEqual(self.__csv_optim, load(tmp, optimize=True))
        os.remove(tmp)

    def test_xlsx_in_and_out(self):
        import SaveDictToFile
        tmp = SaveDictToFile.save_to_xlsx(self.__xls)
        self.assertEqual(self.__xls, load(tmp))
        self.assertEqual(self.__xls_main, load(tmp, maincolumn='#'))
        # self.assertEqual(self.__xls_recogn, load(tmp, recognize=True))  # Todo int+float
        self.assertEqual(self.__xls_optim, load(tmp, optimize=True))
        os.remove(tmp)


if __name__ == '__main__':
    unittest.main()
