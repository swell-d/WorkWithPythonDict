import functools
import time


def print_run_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f'done in {round(time.time() - start_time, 1)} seconds')  # {func.__name__}
        return result

    return wrapper
