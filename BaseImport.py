import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment
from selenium.webdriver.common.action_chains import ActionChains

from GlobalFunctions import print, print_run_time
from LoadDictFromFile import LoadDictFromFile
from Parsing import Parsing
from SaveDictToFile import SaveDictToFile
from TextCorrections import FindDigits, Html, TextCorrections as Sw
from WorkWithJSON import WorkWithJSON
from my_modules2 import param_list_extend
from parsing_classes import Category, Product
