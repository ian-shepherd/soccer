#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Tue Jan 19 2021
#Last updated Fri Jan 29 2021

#@author: Shepherd, Ian

#Sources:
    #Transfermarkt
#Input Data: csv of player urls
#Output: csv of player metadata
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
import numpy as np
import re
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
current_players = pd.read_csv(currentFolder + 'player_metadata.csv')

# Filter players in dataset
players = players.merge(current_players.loc[:,['id']], how='left', left_on='transfermarkt', right_on='id')
players = players[players['id'].isnull()]


# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
# Prep Data
players['t_name'] = players['url'].str.split('/').str[1]



#~~~~~SCRAPE DATA~~~~~

def get_metadata(url, player_id, player_name):

    page = 'https://www.transfermarkt.com' + url
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    birth_date = pageSoup.find('span', {'itemprop' : 'birthDate'}).text.strip()
    birth_date = birth_date.split('\t')[0]
    
    try:
        birth_place = pageSoup.find('span', {'itemprop' : 'birthPlace'}).text
    except:
        birth_place = np.nan
    
    try:
        nationality = pageSoup.find('span', {'itemprop' : 'nationality'}).text
    except:
        nationality = np.nan

    try:
        height = pageSoup.find('span', {'itemprop' : 'height'}).text
    except:
        height = np.nan
    
    
    # position = pageSoup.find('span', text='Position:')
    # position = position.find_next('span').text.strip()
    
    
    club = pageSoup.find('div', {'class' : 'dataZusatzbox'})
    club = club.find('img', alt=True)['alt']
    
    try:
        joined = pageSoup.find('span', text='Joined:')
        joined = joined.find_next('span').text
    except:
        joined = np.nan
    
    
    try:
        contracted = pageSoup.find('span', text='Contract until:')
        contracted = contracted.find_next('span').text
    except:
        contracted = np.nan
    
    try:
        value = pageSoup.find('div', {'class' : 'dataMarktwert'}).text
        updated = re.search('(?<=update: ).*$', value).group()
        value = value.split(' ')[0].strip()
    except:
        value = np.nan
        updated = np.nan

    
    df = pd.DataFrame({'id': player_id,
                       'name' : player_name,
                       'born' : birth_date,
                       'birth_place' : birth_place,
                       'nationality' : nationality,
                       'height' : height,
                       'club' : club,
                       'joined' : joined,
                       'contracted' : contracted,
                       'mv' : value,
                       'update' : updated}, index=[0])
    
    
    return df


errors = []
dfMeta = pd.DataFrame(columns=['id', 'name', 'born', 'birth_place', 'nationality',
                               'height', 'club', 'joined', 'contracted', 'mv', 'update'])

for i in range(0,len(players)): 
    
    url = players.iloc[i,3]
    name = players.iloc[i,5]
    id_ = players.iloc[i,2]
    
    try:
        meta = get_metadata(url, id_, name)
        
        dfMeta = pd.concat([dfMeta, meta])
        print(str(i) + ") " + name + " done")
        time.sleep(random.randint(3,9))
    except:
        errors.append(url)
        print(name, "ERROR")
    
       
dfMeta.to_csv(outputFolder + 'transfermarkt_player_meta.csv', index=False)

dfErrors = pd.DataFrame(errors, columns=['url'])
dfErrors.to_csv(outputFolder + 'transfermarkt_player_meta_errors.csv', index=False)
