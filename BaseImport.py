import time
import urllib.parse

import bs4

import Category
import Product
import Sw
import WorkWithJSON
from Deepl import Deepl
from GlobalFunctions import print
from LoadDictFromFile import LoadDictFromFile
from Parsing import Parsing
from SaveDictToFile import SaveDictToFile
from TextCorrections import FindDigits, Html
from my_modules2 import param_list_extend

# from selenium.webdriver.common.action_chains import ActionChains

if __name__ == '__main__':  # need for "Optimize imports"
    time.time()
    urllib.parse.urljoin()
    bs4.BeautifulSoup()
    bs4.Comment()
    # ActionChains()
    Deepl()
    print()
    LoadDictFromFile()
    Parsing()
    SaveDictToFile()
    FindDigits()
    Html()
    Sw()
    WorkWithJSON.load_dict_from_json()
    param_list_extend()
    Category()
    Product()
