import functools
import time

import SwPrint


def print_run_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        func_without_datetime = ['_xlsx_import', '_xls_import', '_csv_import', 'save_to_xlsx', 'save_to_csv']
        SwPrint.SwPrint.print(f'done in {generate_time_string(time.time() - start_time)}',
                              without_datetime=func.__name__ in func_without_datetime)
        return result

    return wrapper


def print(*args, only_debug=False, end='\n'):
    if SwPrint.SwPrint._start_time == '':
        SwPrint.SwPrint(debug=False, prj_name='')
    SwPrint.SwPrint.print(*args, only_debug=only_debug, end=end)


def generate_time_string(duration):
    hours, min, sec = duration // 3600, duration % 3600 // 60, duration % 60
    text = f'{round(sec, 1)} seconds'
    if min: text = f"{int(min)} minute{'s' if min > 1 else ''} {text}"
    if hours: text = f"{int(hours)} hour{'s' if hours > 1 else ''} {text}"
    return text
