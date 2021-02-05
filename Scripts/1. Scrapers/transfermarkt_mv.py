# -*- coding: utf-8 -*-

#Created on Tue Jan 19 2021
#Last updated Fri Jan 29 2021

#@author: Shepherd, Ian

#Sources:
    #Transfermarkt
#Input Data: csv of player urls
#Output: csv of historical market value
#
#
#
#
#
#

# Packages
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import js2xml
import time
import random

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
dataFolder = rootFolder + '/Data/'
inputFolder = dataFolder + '/Flat/'
currentFolder = dataFolder + '3. Current/2. Cleaned/transfermarkt/'
outputFolder = dataFolder + '2. Update/1. Raw/transfermarkt/'

# Load data
players = pd.read_csv(inputFolder + 'player_translation.txt')
current_players = pd.read_csv(currentFolder + 'player_mv_history.csv')

# Filter players in dataset
players = players.merge(current_players.loc[:,['id']], how='left', left_on='transfermarkt', right_on='id')
players = players[players['id'].isnull()]


# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
# Prep Data
players['t_name'] = players['url'].str.split('/').str[1]



#~~~~~SCRAPE DATA~~~~~

def get_highchart(url, player_id):
    
    page = 'https://www.transfermarkt.com' + url
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    script = pageSoup.find("script", text=re.compile("Highcharts.Chart")).text
    parsed = js2xml.parse(script)
    
    date = parsed.xpath('//property[@name="datum_mw"]//string/text()')
    team = parsed.xpath('//property[@name="verein"]//string/text()')
    value = parsed.xpath('//property[@name="y"]//number/@value')

    idList = []
    dateList = []
    teamList = []
    valueList = []
    
    for i in range(0,len(date)):
        idList.append(str(player_id))
        dateList.append(str(date[i]))
        teamList.append(str(team[i]))
        valueList.append(str(value[i]))
        
    
    df = pd.DataFrame(list(zip(idList, dateList, teamList, valueList)),
                      columns =['id', 'date', 'team', 'value'])

    return df



errors = []
dfMV = pd.DataFrame(columns=['id', 'date', 'team', 'value'])

for i in range(0,len(players)): 
    
    url = players.iloc[i,3]
    name = players.iloc[i,5]
    id_ = players.iloc[i,2]
    
    try:
        mv = get_highchart(url, id_)
    
        dfMV = pd.concat([dfMV, mv])
        print(str(i) + ") " + name + " done")
        time.sleep(random.randint(3,9))
    except:
        errors.append(url)
        print(name, "ERROR")

        

     
dfMV.to_csv(outputFolder + 'transfermarkt_player_mv.csv', index=False)

dfErrors = pd.DataFrame(errors, columns=['url'])
dfErrors.to_csv(outputFolder + 'transfermarkt_player_mv_errors.csv', index=False)