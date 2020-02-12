import datetime
import json

import requests
import win32api

print('\n===', datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M"), 'WinTime')

try:
    result = json.loads(requests.get('http://worldtimeapi.org/api/timezone/Etc/GMT').content)
    time = datetime.datetime.fromtimestamp(result['unixtime'] - 60 * 60 * 3)
    time_tuple = (time.year, time.month, time.day, time.hour, time.minute, time.second, 0)
    print(time_tuple)
    dayOfWeek = datetime.datetime(*time_tuple).isocalendar()[2]
    t = time_tuple[:2] + (dayOfWeek,) + time_tuple[2:]
    win32api.SetSystemTime(*t)
    print('ok')
except:
    print('error')
