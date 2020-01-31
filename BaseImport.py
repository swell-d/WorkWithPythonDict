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
