import codecs
import copy
import os
import pathlib
import re
import unittest
from datetime import datetime

from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from GlobalFunctions import print, print_run_time


class SaveDictToFile:
    @classmethod
    def __init(cls, data, filename, fieldnames):
        if fieldnames is None: fieldnames = []
        if not isinstance(data, (dict, list)): raise ValueError('Wrong data')
        if not isinstance(filename, str): raise ValueError('Wrong filename')
        if not isinstance(fieldnames, list): raise ValueError('Wrong fieldnames')
        for key in fieldnames:
            if not isinstance(key, str): raise ValueError('Wrong fieldnames')
        data = copy.deepcopy(data)
        fieldnames = cls.__generate_fieldnames(data, fieldnames)
        return data, fieldnames

    @classmethod
    def __generate_fieldnames(cls, data, fieldnames):
        new_fieldnames = []
        for each in data.values() if isinstance(data, dict) else data:
            if not isinstance(each, dict): raise ValueError('Wrong data')
            for key, value in each.items():
                if value != '' and key not in new_fieldnames: new_fieldnames.append(str(key))
        if '#' in new_fieldnames: new_fieldnames.remove('#')
        additional_fields = [x for x in new_fieldnames if x not in fieldnames]
        cleared_fields = [x for x in fieldnames if x not in new_fieldnames]
        if cleared_fields: print('deleted columns: ' + ', '.join(cleared_fields))
        return [x for x in fieldnames if x in new_fieldnames] + additional_fields

    @classmethod
    def __view_enhancement(cls, ws):
        def auto_column_width():
            dims = {}
            for row in ws.iter_rows():
                for cell in row:
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 1), len(str(cell.value))))
            for col, value in dims.items():
                ws.column_dimensions[col].width = min(value + 2, 40)

        ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
        ws.freeze_panes = ws['A2']
        auto_column_width()

    @classmethod
    @print_run_time
    def save_to_xlsx(cls, data, filename='', fieldnames=None, optimize=False, open=False, date_insert=True):
        if not cls.__check_data(data, filename): return None
        data, fieldnames = cls.__init(data, filename, fieldnames)
        newfilename = cls.get_new_file_name_with_datetime('.xlsx', filename, date_insert)
        wb = Workbook()
        ws = wb.active
        ws.append(['#'] + fieldnames)
        i = -1
        for i, each in enumerate(data.values() if isinstance(data, dict) else data):
            line = [i + 1]
            for key in fieldnames:
                value = each.get(key, '')
                if not isinstance(value, (int, float)) or len(str(value)) > 10:
                    value = str(value) if not optimize else re.sub(r'\s+', ' ', str(value)).strip()
                line.append(value)
            ws.append(line)
        cls.__view_enhancement(ws)
        wb.save(newfilename)
        print(f"{newfilename} / {i + 1} lines saved / ", end='')
        if open: os.startfile(newfilename)
        return newfilename

    @classmethod
    def __check_data(cls, data, filename):
        if data: return True
        print(f'{filename} / nothing to save / ', end='')
        return False

    @classmethod
    def get_new_file_name_with_datetime(cls, filetype, filename, date_insert):
        if not date_insert:
            if '\\' in filename: pathlib.Path(filename[:filename.rfind('\\')]).mkdir(parents=True, exist_ok=True)
            return f'{filename}{filetype}'
        date = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
        if '\\' not in filename: return f'{date}_{filename}{filetype}'
        last_pos = filename.rfind('\\')
        pathlib.Path(filename[:last_pos]).mkdir(parents=True, exist_ok=True)
        return f'{filename[:last_pos]}\\{date}_{filename[last_pos + 1:]}{filetype}'

    @classmethod
    @print_run_time
    def save_to_csv(cls, data, filename='', fieldnames=None, optimize=False, open=False, date_insert=True):
        if not cls.__check_data(data, filename): return None
        SEP, QC, NL = ',', '"', '\r\n'  # separator, quote char, new line
        data, fieldnames = cls.__init(data, filename, fieldnames)
        newfilename = cls.get_new_file_name_with_datetime('.csv', filename, date_insert)
        with codecs.open(newfilename, 'w', encoding='utf-8') as file:
            fieldnames.insert(0, '#')
            file.write(SEP.join([f'{QC}{x}{QC}' for x in fieldnames]) + NL)
            i = -1
            for i, each in enumerate(data.values() if isinstance(data, dict) else data):
                line = [i + 1]
                for key in fieldnames[1:]:
                    value = each.get(key, '')
                    if isinstance(value, float): value = str(value).replace('.', ',')
                    value = str(value) if not optimize else re.sub(r'\s+', ' ', str(value)).strip()
                    line.append(value.replace('"', '""'))
                file.write(SEP.join([f'{QC}{x}{QC}' for x in line]) + NL)
        print(f"{newfilename} / {i + 1} lines saved / ", end='')
        if open: os.startfile(newfilename)
        return newfilename

    # @classmethod
    # @print_run_time
    # def _save_to_csv_old(cls, data, filename='', fieldnames=None, optimize=False):
    #     data, fieldnames = cls.__init(data, filename, fieldnames)
    #     with codecs.open(f'{cls.__DATE}_{filename}.csv', 'w', encoding='utf-8') as file:
    #         writer = csv.DictWriter(file, fieldnames=fieldnames)
    #         writer.writeheader()
    #         for each in data.values() if isinstance(data, dict) else data:
    #             for key in list(each).copy():
    #                 if key not in fieldnames: del each[key]
    #             for key in fieldnames:
    #                 if key not in each: each[key] = ''
    #             writer.writerow(each)

    @classmethod
    def save_to_files(cls, data, filename='', fieldnames=None, optimize=False, open=False, date_insert=True):
        cls.save_to_xlsx(data, filename, fieldnames, optimize, open, date_insert)
        cls.save_to_csv(data, filename, fieldnames, optimize, open, date_insert)


class SaveDictToFileTests(unittest.TestCase):
    __data = {'elem1': {'first': '1\r\n1', 'second': 22.2},
              'elem2': {'second': 12345678901234567890, 'third': '"4""4', 'fourth': ''}}
    __data_xlsx = {'1': {'#': 1, 'first': '1\r\n1', 'second': 22.2, 'third': ''},
                   '2': {'#': 2, 'first': '', 'second': '12345678901234567890', 'third': '"4""4'}}
    __data_csv = {'1': {'#': 1, 'first': '1\r\n1', 'second': '22,2', 'third': ''},
                  '2': {'#': 2, 'first': '', 'second': 12345678901234567890, 'third': '"4""4'}}

    def test_save_to_xlsx(self):
        file_name = f'{datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")}_.xlsx'
        result = [['#', 'first', 'second', 'third'], ['1', '1\r\n1', '22.2', 'None'],
                  ['2', 'None', '12345678901234567890', '"4""4']]
        xlsx = []
        SaveDictToFile.save_to_xlsx(self.__data)
        sheet = load_workbook(file_name).active
        for row in range(1, sheet.max_row + 1):
            row_data = []
            for column in range(1, sheet.max_column + 1):
                row_data.append(str(sheet.cell(row=row, column=column).value))
            xlsx.append(row_data)
        self.assertEqual(result, xlsx)
        from LoadDictFromFile import LoadDictFromFile
        self.assertEqual(self.__data_xlsx, LoadDictFromFile.load(file_name, recognize=True))
        self.assertEqual(self.__data_xlsx, LoadDictFromFile.load(file_name, maincolumn='#', recognize=True))
        os.remove(file_name)

    def test_save_to_csv(self):
        file_name = f'{datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")}_.csv'
        result = '"#","first","second","third"\r\n"1","1\r\n1","22,2",""\r\n"2","","12345678901234567890","""4""""4"\r\n'
        SaveDictToFile.save_to_csv(self.__data)
        with codecs.open(file_name, 'r', encoding='utf-8') as file:
            csv = file.read()
        self.assertEqual(result, csv)
        from LoadDictFromFile import LoadDictFromFile
        self.assertEqual(self.__data_csv, LoadDictFromFile.load(file_name, recognize=True))
        self.assertEqual(self.__data_csv, LoadDictFromFile.load(file_name, maincolumn='#', recognize=True))
        os.remove(file_name)

    # def test_save_to_csv_old(self):
    #     file_name = f'{datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")}_old.csv'
    #     result = 'first,second,third\r\n"1\r\n1",22.2,\r\n,12345678901234567890,"""4""""4"\r\n'
    #     SaveDictToFile._save_to_csv_old(self.__data, filename='old')
    #     with codecs.open(file_name, 'r', encoding='utf-8') as file:
    #         csv = file.read()
    #     self.assertEqual(result, csv)
    #     os.remove(file_name)

    def test_get_new_file_name(self):
        date = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
        self.assertEqual('filename.xlsx',
                         SaveDictToFile.get_new_file_name_with_datetime('.xlsx', 'filename', date_insert=False))
        self.assertEqual(f'{date}_filename.xlsx',
                         SaveDictToFile.get_new_file_name_with_datetime('.xlsx', 'filename', date_insert=True))
        self.assertEqual('C:\\tmp\\filename.xlsx',
                         SaveDictToFile.get_new_file_name_with_datetime('.xlsx', 'C:\\tmp\\filename',
                                                                        date_insert=False))
        self.assertEqual(f'C:\\tmp\\{date}_filename.xlsx',
                         SaveDictToFile.get_new_file_name_with_datetime('.xlsx', 'C:\\tmp\\filename', date_insert=True))

if __name__ == '__main__':
    unittest.main()
