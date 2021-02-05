#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Oct 31 2020
#Last updated Tue Jan 26 2021

#@author: ishepher

#Sources:
    #fbref
#Output: csv of matches urls for big 5 leagues and CL/Europa for current season
#
#
#
#
#
#
#~~~~~~INITIAL SETUP~~~~~~

# Packages
import os
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
outputFolder = rootFolder + '/Data/2. Update/Flat/'

# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    

    

#~~~~~SCRAPE DATA~~~~~
    
def get_match_urls(page, href_col):
    
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')

    table = pageSoup.find('table')
    tbody = table.find('tbody')
    tr = tbody.find_all('tr')
    
    match_urls = []
    
    for row in range(0,len(tr)):
        
        url = tr[row].find_all('a', href=True)
        
        if len(url) == href_col + 1:
            match_urls.append(url[href_col]['href'])
        
    print(page, 'done')
            
    return match_urls

# urls and match url href column
urls = {'https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures' : 4,
        'https://fbref.com/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures' : 4,
        'https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures' : 4, #change when get to playoffs
        'https://fbref.com/en/comps/11/schedule/Serie-A-Scores-and-Fixtures' : 4,
        'https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures' : 4,
        'https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures' : 5,
        'https://fbref.com/en/comps/19/schedule/Europa-League-Scores-and-Fixtures' : 3}


# iterate through dictionary and add to list
match_urls = []

for key in urls:
    match_urls.extend(get_match_urls(key, urls[key]))
    time.sleep(5)
  
# save as csv
df = pd.DataFrame(data = match_urls, columns=['urls'])
df.to_csv(outputFolder + 'match_urls.csv', index=False)
