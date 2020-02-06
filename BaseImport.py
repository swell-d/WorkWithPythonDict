import time
import urllib.parse

import bs4

import Category
import LoadDictFromFile
import Product
import SaveDictToFile
import Sw
import WorkWithJSON
from Deepl import Deepl
from GlobalFunctions import print
from Parsing import Parsing
from TextCorrections import FindDigits, Html
from my_modules2 import param_list_extend


# from selenium.webdriver.common.action_chains import ActionChains

def tmp():  # need for "Optimize imports"
    time()
    urllib()
    bs4()
    Category()
    Product()
    Sw()
    WorkWithJSON()
    Deepl()
    print()
    LoadDictFromFile()
    Parsing()
    SaveDictToFile()
    FindDigits()
    Html()
    param_list_extend()
