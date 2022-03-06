# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 16:38:05 2022

@author: NAUSHEEN TABASSUM
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

# List of names of companies - remove dupes & NULL values
full_list = pd.read_csv('european_list.csv', header = 0)
euro_list = full_list.drop_duplicates(subset = ['instrumentname'])
euro_list = euro_list.dropna(axis = 0)
euro_list = euro_list.reset_index(drop = True)
euro_list[['search terms', 'links - t1', 'CUSIP number']] = ""

# Split names to search terms
for i in range(len(euro_list['instrumentname'])):
    x = euro_list['instrumentname'][i].split(' ')
    euro_list['search terms'][i] = x



### Dividing full data frame into 5 portions
df1 = euro_list[0:500]
df2 = euro_list[501:1000]
df3 = euro_list[1001:1500]
df4 = euro_list[1501:2000]
df5 = euro_list[2001:2446]

# Function to get links:
    # Search using the first term only
    # Collects all links based on partial match
    # Goes into link only containing cusip (to differentiate between 'investment' and 'managers')
    # Collects 13F filing counts for each links
    # Adds link with maximum value to the df
  
def search_func(df, t):
    r = df.index.values.astype(int)
    m = r[0]
    n = r[len(r)-1]
    
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(ChromeDriverManager().install(),
                              chrome_options = chrome_options)

    for j in range(m,n):
        a = df['search terms'][j][t]
        driver.get("https://13f.info/search?q=" + a)
        result = driver.find_element_by_tag_name("h2").get_attribute("innerText")
        if result == "No results found":
            continue
        else:
            try:
                links = driver.find_elements_by_partial_link_text(a.upper())
            except NoSuchElementException:
                    continue
            all_links = []
            sum_for_links = []
            for l in links:
                hlink = l.get_attribute("href")
                all_links.append(hlink)
                all_links = [string for string in all_links if 'cusip' in string]
            for i in all_links:
                driver.get(i)
                filings = driver.find_elements_by_xpath("//td[@class]")
                filing_counts = []
                for k in filings:
                    count = k.get_attribute("innerText")
                    try:
                        filing_counts.append(int(count))
                    except ValueError:
                        continue
                total = sum(filing_counts)
                sum_for_links.append(total)
            all_filingcounts = pd.DataFrame({'URL': all_links,
                                'Filing counts': sum_for_links})
            link_to_keep = all_filingcounts[all_filingcounts['Filing counts'] ==
                                max(all_filingcounts['Filing counts'], default = 0)]['URL']
        euro_list['links'][j] = link_to_keep.values
    driver.quit()
        
# Open Selenium driver
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install(),
                              chrome_options = chrome_options)

# Running the function for all 
search_func(df1)
search_func(df2)
search_func(df3)
search_func(df4)
search_func(df5)

 
# Loop to get cusip numbers from the link and add to df      
for c in range(len(euro_list['links'])):
    cusip = re.findall('(?<=cusip/).*', str(euro_list['links'][c]))
    number = re.sub(r'[^\w\s]', '', str(cusip))
    euro_list['CUSIP number'][c] = number


# Results to .csv
euro_list.to_csv("Search results.csv")
