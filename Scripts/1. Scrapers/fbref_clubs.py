#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Jan 2 2021
#Last updated 

#@author: ishepher

#Sources:
    #fbref
#Output: club logos as png for big 5 leagues (2017-2020) and CL/Europa (2018-2020)
#
#
#
#
#
#
#~~~~~~INITIAL SETUP~~~~~~

# Packages
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(__file__))
inputFolder = rootFolder + '/Transformed Data/'
outputFolder = rootFolder + '/Club Logos/'

# Import data
teams = pd.read_csv(inputFolder + 'team_countries.csv')
team_ids = teams['id']

# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    
    
#~~~~~SCRAPE LOGOS~~~~~

def get_logos(page, team_name, team_id):
    
    path = outputFolder + team_name + '.png'
    
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    logo = pageSoup.find('img', {'class' : 'teamlogo'})
    response = requests.get(logo['src'])
    file = open(path, 'wb')
    file.write(response.content)
    file.close()
    
 
    
for i in team_ids:
    team_name = teams[teams['id']==i]['name'].item()
    page = 'https://fbref.com/en/squads/' + i + '/'
    
    get_logos(page, team_name, i)
    print(team_name, 'done')
    time.sleep(random.randint(3,9))