import functools
import time

from SwPrint import SwPrint


def print_run_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f'done in {round(time.time() - start_time, 1)} seconds')  # {func.__name__}
        return result

    return wrapper


def print(text, only_debug=False, end='\n'):
    SwPrint.print(text, only_debug, end)
