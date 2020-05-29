import time
import urllib.parse
from datetime import datetime
from urllib.parse import quote, urljoin

import bs4

import Category
import Deepl
import FindDigits
import Html
import LoadDictFromFile
import Parsing
import Product
import SaveDictToFile
import Sw
import WorkWithJSON
from GlobalFunctions import print


# from SaveDictToFile import _param_list_extend as param_list_extend
# from selenium.webdriver.common.action_chains import ActionChains

def tmp():  # need for "Optimize imports"
    time()
    urllib()
    bs4()
    Category()
    Deepl()
    FindDigits()
    Html()
    LoadDictFromFile()
    Parsing()
    Product()
    SaveDictToFile()
    Sw()
    WorkWithJSON()
    print()
    datetime()
    quote()
    urljoin()
