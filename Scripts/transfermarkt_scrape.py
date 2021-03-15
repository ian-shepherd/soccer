#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Tue Jan 19 2021
#Last updated Sat Feb 20 2021

#@author: Shepherd, Ian

#Sources:
    #Transfermarkt
#Input Data: csv of missing player urls
#Output: csvs of player metadata, historical market value, and transfers
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
import js2xml
import time
import random

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(__file__))
dataFolder = rootFolder + '/Data/'
inputFolder = dataFolder + 'Flat/'
dbFolder = dataFolder + 'Database/'
outputFolder = dataFolder + 'Update/'

# Load data
players = pd.read_csv(inputFolder + 'player_translation.txt')
db_players = pd.read_csv(dbFolder + 'trans_player_dim.csv')

# Filter players in dataset
players = players.merge(db_players.loc[:,['id']], how='left', left_on='transfermarkt', right_on='id')
players = players[players['id'].isnull()]


# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    
# Filter deceased players
players = players[~players['url'].isin(['/davide-astori/profil/spieler/87210',
                                        '/emiliano-sala/profil/spieler/190780'])]
    
# Prep Data
players['t_name'] = players['url'].str.split('/').str[1]


#~~~~~SCRAPER FUNCTIONS~~~~~
    
def get_metadata(pageSoup, url, player_id, player_name):
    
    
    player_data = pageSoup.find('div', {'class' : 'spielerdaten'})
    player_table = player_data.find('table', {'class' : 'auflistung'})
    
    
    headshot_url = pageSoup.find('div', {'class' : 'dataBild'})
    headshot_url = headshot_url.find('img')['src']
    
    
    try:
        full_name = player_table.find('th', text='Name in home country:').find_next('td').text.strip()
    except:
        try:
            full_name = player_table.find('th', text='Full name:').find_next('td').text.strip()
        except:
            full_name = np.nan
    
    
    try:
        birth_date = player_table.find('th', text='Date of birth:').find_next('td').text.strip()
    except:
        birth_date = np.nan
    
    try:
        birth_place = player_table.find('th', text='Place of birth:').find_next('td').text.strip()
    except:
        birth_place = np.nan
    
    
    try:
        height = player_table.find('th', text='Height:').find_next('td').text.strip()
    except:
        height = np.nan
    
    try:
        nationality = player_table.find('th', text='Citizenship:').find_next('td').text.strip()
        nationality = re.split(r'\s{2,}', nationality)
    except:
        nationality = np.nan
         
    try:
        position = player_table.find('th', text='Position:').find_next('td').text.strip()
    except:
        position = np.nan
         
    try:
        foot = player_table.find('th', text='Foot:').find_next('td').text.strip()
    except:
        foot = np.nan
    
    
    try:
        position_data = pageSoup.find('div', {'class' : 'detailpositionen'})
        position_data = position_data.find('div', {'class': 'auflistung'})
        position_data_main = position_data.find('div', {'class': 'hauptposition-left'})
        position_main = re.findall(':(.*)', position_data_main.text)[0].strip()
    except:
        position_main = np.nan
        
    try:
        position_data_alt = position_data.find('div', {'class': 'nebenpositionen'})
        position_data_alt = re.split(r'\s{2,}', position_data_alt.text)
        position_data_alt[0] = position_data_alt[0].strip()
        pos_alt1 = position_data_alt[0].split('\n')[1]
        pos_alt2 = position_data_alt[1] if position_data_alt[1] != '' else np.nan
    except:
        pos_alt1 = np.nan
        pos_alt2 = np.nan
    


    
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
    
    
    
    
    
    df = pd.DataFrame({'id' : player_id,
                       'name' : player_name,
                       'url' : url,
                       'headshot_url' : headshot_url,
                       'full_name' : full_name,
                       'born' : birth_date,
                       'birth_place' : birth_place,
                       'height' : height,
                       'nationality' : nationality[0],
                       'position' : position,
                       'position_main' : position_main,
                       'position_alt1' : pos_alt1,
                       'position_alt2' : pos_alt2,
                       'foot' : foot,
                       'club' : club,
                       'joined' : joined,
                       'contracted' : contracted,
                       'mv' : value,
                       'update' : updated}, index=[0])                     
        

    
    return df



def get_highchart(pageSoup, player_id):
    
    script = pageSoup.find("script", text=re.compile("Highcharts.Chart")).string
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



def scrape_data(url, player_id, player_name):
    
    page = 'https://www.transfermarkt.com' + url
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    
    metadata = get_metadata(pageSoup, url, player_id, player_name)
    mv = get_highchart(pageSoup, player_id)
    transfers = get_transfers(url.replace('profil', 'transfers'), player_id)
    
    
    return metadata, mv, transfers



#~~~~~SCRAPE DATA~~~~~
    
# Create empty dataframes
errors = []
dfMeta = pd.DataFrame(columns=['id', 'name', 'url', 'headshot_url', 'full_name', 'born', 'birth_place',
        'height', 'nationality', 'position', 'position_main', 'position_alt1',
        'position_alt2', 'foot', 'club', 'joined', 'contracted', 'mv',
        'update'])
dfMV = pd.DataFrame(columns=['id', 'date', 'team', 'value'])
dfTransfers = pd.DataFrame(columns=['id', 'season', 'date', 'left', 'joined', 'value', 'fee'])


# for i in range(0,len(players)): 
    
#     url = players.iloc[i,3]
#     name = players.iloc[i,5]
#     id_ = players.iloc[i,2]
    
    
#     try:
#         df = scrape_data(url, id_, name)
        
#         dfMeta = pd.concat([dfMeta, df[0]])
#         dfMV = pd.concat([dfMV, df[1]])
#         dfTransfers = pd.concat([dfTransfers, df[2]])
        
#         print(str(i) + ") " + name + " done")
#         time.sleep(random.randint(3,9))
#     except:
#         errors.append(url)
#         print(name, "ERROR")
        


# Export data
# dfMeta.to_csv(outputFolder + 'raw_transfermarkt_player_meta.csv', index=False)
# dfMV.to_csv(outputFolder + 'raw_transfermarkt_player_mv.csv', index=False)
# dfTransfers.to_csv(outputFolder + 'raw_transfermarkt_player_transfers.csv', index=False)

# dfErrors = pd.DataFrame(errors, columns=['url'])
# dfErrors.to_csv(outputFolder + 'raw_transfermarkt_player_meta_errors.csv', index=False)
