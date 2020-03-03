import codecs
import datetime
import pathlib


class SwPrint:
    __log = ''
    __debug = False
    __prj_name = ''
    __path = ''
    _start_time = ''

    @classmethod
    def __init__(cls, debug=False, prj_name='', path='C:\\_cache\\__logs\\'):
        cls.__debug = debug
        cls.__prj_name = prj_name
        cls.__path = path
        cls._start_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H-%M")

    @classmethod
    def print(cls, *args, only_debug=False, end='\n', without_datetime=False):
        if not cls.__debug and only_debug: return
        new_text = f'{datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H:%M:%S")}  ' if not without_datetime else ''
        new_text += f'{" ".join([str(txt) for txt in args])}{end}'
        print(new_text, end='')
        cls.__log += new_text
        # cls.save_log_to_file()

    @classmethod
    def save_log_to_file(cls):
        full_path = f'{cls.__path}\\{cls._start_time}_{cls.__prj_name}'.rstrip('_') + '.txt'
        pathlib.Path(cls.__path).mkdir(parents=True, exist_ok=True)
        with codecs.open(full_path, 'w', 'utf-8') as f:
            f.write(cls.__log)
