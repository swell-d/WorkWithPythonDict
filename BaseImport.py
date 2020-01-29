import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment

import Sw
import WorkWithJSON
from Deepl import Deepl
from GlobalFunctions import print, print_run_time
from LoadDictFromFile import LoadDictFromFile
from Parsing import Parsing
from SaveDictToFile import SaveDictToFile
from TextCorrections import FindDigits, Html
from my_modules2 import param_list_extend

# from selenium.webdriver.common.action_chains import ActionChains

if __name__ == '__main__':  # need for "Optimize imports"
    time.time()
    urljoin()
    BeautifulSoup()
    Comment()
    # ActionChains()
    Deepl()
    print()
    print_run_time()
    LoadDictFromFile()
    Parsing()
    SaveDictToFile()
    FindDigits()
    Html()
    Sw()
    WorkWithJSON.load_dict_from_json('')
    param_list_extend()
