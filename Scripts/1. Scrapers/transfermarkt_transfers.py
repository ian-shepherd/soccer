#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Tue Jan 19 2021
#Last updated Tue Feb 16 2021

#@author: Shepherd, Ian

#Sources:
    #Transfermarkt
#Input Data: csv of player urls
#Output: csv of transfers
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
import time
import random

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
dataFolder = rootFolder + '/Data/'
inputFolder = dataFolder + '/Flat/'
dbFolder = dataFolder + '3. Current/3. Database/'
outputFolder = dataFolder + '2. Update/1. Raw/transfermarkt/'

# Load data
players = pd.read_csv(inputFolder + 'player_translation.txt')
db_players = pd.read_csv(dbFolder + 'trans_transfer_fact.csv')

# Filter players in dataset
db_players = db_players.loc[:,['id']].drop_duplicates()
players = players.merge(db_players.loc[:,['id']], how='left', left_on='transfermarkt', right_on='id')
players = players[players['id'].isnull()]


# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
# Prep Data
players['t_name'] = players['url'].str.split('/').str[1]


#~~~~~SCRAPE DATA~~~~~

def get_transfers(url, player_id):
    
    page = 'https://www.transfermarkt.com' + url
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    table = pageSoup.find('table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    idList = []
    seasonList = []
    dateList = []
    leftList = []
    joinedList = []
    mvList = []
    feeList = []
    
    
    for row in rows:
        
        if any(x in row.text for x in ['Upcoming transfer', 'Transfer history']):
            continue


        dates = row.find_all('td', {'class' : 'zentriert'})
        season = dates[0].text
        date = dates[1].text
        
        teams = row.find_all('td', {'class' : 'no-border-rechts vereinswappen'})
        left = teams[0].find('img', alt=True)['alt']
        joined = teams[1].find('img', alt=True)['alt']
        
        mv = row.find('td', {'class' : 'zelle-mw'}).text
        fee = row.find('td', {'class' : 'zelle-abloese'}).text
        
        
        idList.append(player_id)
        seasonList.append(season)
        dateList.append(date)
        leftList.append(left)
        joinedList.append(joined)
        mvList.append(mv)
        feeList.append(fee)
    

    df = pd.DataFrame(list(zip(idList, seasonList, dateList, leftList, joinedList, mvList, feeList)),
                      columns =['id', 'season', 'date', 'left', 'joined', 'value', 'fee'])
    
    return df



errors = []
dfTransfers = pd.DataFrame(columns=['id', 'season', 'date', 'left', 'joined', 'value', 'fee'])

for i in range(0,len(players)): 
    
    url = players.iloc[i,3].replace('profil', 'transfers')
    name = players.iloc[i,5]
    id_ = players.iloc[i,2]
    
    try:
        transfers = get_transfers(url, id_)
    
        dfTransfers = pd.concat([dfTransfers, transfers])
        print(str(i) + ") " + name + " done")
        time.sleep(random.randint(3,9))
    except:
        errors.append(url)
        print(name, "ERROR")
    

dfTransfers.to_csv(outputFolder + 'transfermarkt_player_transfers.csv', index=False)

dfErrors = pd.DataFrame(errors, columns=['url'])
dfErrors.to_csv(outputFolder + 'transfermarkt_player_transfers_errors.csv', index=False)