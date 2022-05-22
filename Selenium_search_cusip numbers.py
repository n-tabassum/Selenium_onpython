# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 20:27:43 2022

@author: NAUSHEEN TABASSUM
"""


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

# List of cusip numbers - removing NULL values, adding columns
full_list = pd.read_csv('cusip_list.csv', header = 0)
full_list[['name', 'symbol', 'class', 'type', 'filings']] = ""
full_list = full_list.dropna(axis = 0)
full_list = full_list.reset_index(drop = True)

# Open selenium webdriver
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(),
                          chrome_options = chrome_options)

# Search using cusip numbers:
for i in range(0, len(full_list)):
    driver.get('https://13f.info/search?q=' + full_list['cusip'][i])
    result = driver.find_element_by_tag_name('h2').get_attribute("innerText")
    if result == "No results found":
        continue
    else:
        link = driver.find_element_by_tag_name('ul').click()
        filings = driver.find_element_by_tag_name('tbody').get_attribute("innerText")
        full_list['filings'][i] = filings.split('\n')
        page = driver.find_element_by_tag_name('html').get_attribute("innerText")
        text = page.split('\n')
        full_list['name'][i] = text[0]
        full_list['type'][i] = text[5]
        full_list['class'][i] = text [7]
        if 'Symbol' in page:
            full_list['symbol'][i] = text[3]
        else:
            continue

driver.quit()

# Arranging filings as dictionary
for j in range(0, len(full_list)):
    n = len(full_list['filings'][j])
    x = {}
    for k in range(0, n):
        key = full_list['filings'][j][k].split('\t')
        full_list['filings'][j][k] = {key[0]:key[1]}
    for all in full_list['filings'][j]:
        x.update(all)
    if len(x) != 0:
        full_list['filings'][j] = x


# Results to .csv
full_list.to_csv("Search_results_cusip.csv")

