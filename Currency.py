import pathlib
import re
from datetime import datetime

import requests


def get_rate(cur_from, cur_to, date=datetime.strftime(datetime.now(), "%d/%m/%Y")):
    path = f"/var/www/swell/data/www/currency/{date.replace('/', '-')}.xml"

    if not pathlib.Path(path).exists():
        response = requests.get(f"http://www.cbr.ru/scripts/XML_daily.asp", {"date_req": date})
        if response.status_code != 200: raise ConnectionError
        response_content = response.text
        pathlib.Path(path[:path.rfind('/')]).mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as file:
            file.write(response_content)
    else:
        with open(path, 'r') as file:
            response_content = file.read()

    if cur_from == "RUB":
        n1, v1 = 1, 1
    else:
        cur_from_p = re.compile(
            r"<CharCode>" + cur_from + r"</CharCode><Nominal>(\d+)</Nominal><Name>.+?</Name><Value>([\d,]+?)</Value>")
        cur_from_data = re.search(cur_from_p, response_content)
        n1 = float(cur_from_data.group(1))
        v1 = float(cur_from_data.group(2).replace(",", "."))

    if cur_to == "RUB":
        n2, v2 = 1, 1
    else:
        cur_to_p = re.compile(
            r"<CharCode>" + cur_to + r"</CharCode><Nominal>(\d+)</Nominal><Name>.+?</Name><Value>([\d,]+?)</Value>")
        cur_to_data = re.search(cur_to_p, response_content)
        n2 = float(cur_to_data.group(1))
        v2 = float(cur_to_data.group(2).replace(",", "."))

    result = round(v1 / n1 / v2 * n2, 4)
    if not result: raise ConnectionError
    return result


if __name__ == '__main__':
    print('EUR', get_rate('EUR', 'RUB'))
    print('USD', get_rate('USD', 'RUB'))
