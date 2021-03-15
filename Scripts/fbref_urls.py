#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Oct 31 2020
#Last updated Sat Feb 20 2021

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
import pandas as pd
import time
import random


# Folder paths
rootFolder = os.path.dirname(os.path.dirname(__file__))
outputFolder = rootFolder + '/Data/Flat/'

# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
    

#~~~~~SCRAPE DATA~~~~~
    
def get_match_urls(url, href_col):
    
    page = 'https://fbref.com' + url
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
        
            
    return match_urls


# urls and match url href column
urls = {
        # Bundesliga
        '/en/comps/20/1634/schedule/2017-2018-Bundesliga-Scores-and-Fixtures' : 5,
        '/en/comps/20/2109/schedule/2018-2019-Bundesliga-Scores-and-Fixtures' : 5,
        '/en/comps/20/3248/schedule/2019-2020-Bundesliga-Scores-and-Fixtures' : 5,
        '/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures' : 4, #change when get to playoffs
        
        # EPL
        '/en/comps/9/1631/schedule/2017-2018-Premier-League-Scores-and-Fixtures' : 4,
        '/en/comps/9/1889/schedule/2018-2019-Premier-League-Scores-and-Fixtures' : 4,
        '/en/comps/9/3232/schedule/2019-2020-Premier-League-Scores-and-Fixtures' : 4,
        '/en/comps/9/schedule/Premier-League-Scores-and-Fixtures' : 4,
                
        # La Liga
        '/en/comps/12/1652/schedule/2017-2018-La-Liga-Scores-and-Fixtures' : 4,
        '/en/comps/12/1886/schedule/2018-2019-La-Liga-Scores-and-Fixtures' : 4,
        '/en/comps/12/3239/schedule/2019-2020-La-Liga-Scores-and-Fixtures' : 4,
        '/en/comps/12/schedule/La-Liga-Scores-and-Fixtures' : 4,
        
        # Ligue 1
        '/en/comps/13/1632/schedule/2017-2018-Ligue-1-Scores-and-Fixtures' : 5,
        '/en/comps/13/2104/schedule/2018-2019-Ligue-1-Scores-and-Fixtures' : 5,
        '/en/comps/13/3243/schedule/2019-2020-Ligue-1-Scores-and-Fixtures' : 4,
        '/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures' : 4,
        
        # Serie A
        '/en/comps/11/1640/schedule/2017-2018-Serie-A-Scores-and-Fixtures' : 4,
        '/en/comps/11/1896/schedule/2018-2019-Serie-A-Scores-and-Fixtures' : 4,
        '/en/comps/11/3260/schedule/2019-2020-Serie-A-Scores-and-Fixtures' : 4,      
        '/en/comps/11/schedule/Serie-A-Scores-and-Fixtures' : 4,
        
        # Champs League
        '/en/comps/8/2102/schedule/2018-2019-Champions-League-Scores-and-Fixtures' : 5,
        '/en/comps/8/2900/schedule/2019-2020-Champions-League-Scores-and-Fixtures' : 5,
        '/en/comps/8/schedule/Champions-League-Scores-and-Fixtures' : 5,
        
        # Europa
        '/en/comps/19/2103/schedule/2018-2019-Europa-League-Scores-and-Fixtures' : 5,
        '/en/comps/19/2901/schedule/2019-2020-Europa-League-Scores-and-Fixtures' : 5,
        '/en/comps/19/schedule/Europa-League-Scores-and-Fixtures' : 5,
        
        # MLS
        '/en/comps/22/1759/schedule/2018-Major-League-Soccer-Scores-and-Fixtures' : 5,
        '/en/comps/22/2798/schedule/2019-Major-League-Soccer-Scores-and-Fixtures' : 5,
        '/en/comps/22/schedule/Major-League-Soccer-Scores-and-Fixtures' : 5
        #'en/comps/22/11006/schedule/2021-Major-League-Soccer-Scores-and-Fixtures' 2021 4 change to 5
        }


# iterate through dictionary and add to list
match_urls = []

for key in urls:
    match_urls.extend(get_match_urls(key, urls[key]))
    print(key, 'done')
    time.sleep(random.randint(3,9))
  
# # save as csv
df = pd.DataFrame(data = match_urls, columns=['urls'])
df.to_csv(outputFolder + 'match_urls.csv', index=False)


