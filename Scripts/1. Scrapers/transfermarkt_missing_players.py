#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Fri Jan 29 2021
#Last updated 

#@author: ishepher

#Sources:
    #fbref
#Input: csv of match stats
#Output: csvs of players to add to translation table
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


# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
dataFolder = rootFolder + '/Data/'
translationFolder = dataFolder + 'Flat/'
currentFolder = dataFolder + '3. Current/2. Cleaned/fbref/'
updateFolder = dataFolder + '2. Update/2. Cleaned/fbref/'
outputFolder = dataFolder + '2. Update/Flat/'


# Import data
translationDF = pd.read_csv(translationFolder + 'player_translation.txt')
teamsDF = pd.read_csv(translationFolder + 'team_translation.csv')
currentDF = pd.read_csv(currentFolder + 'player_stats.csv')
updateDF = pd.read_csv(updateFolder + 'player_stats.csv')


# Find missing players
players = pd.concat([currentDF, updateDF])
player_teams = players.drop_duplicates(subset=['id'], keep='last')
player_teams = player_teams.loc[:,['id', 'team_id']].merge(teamsDF.loc[:,['fbref', 'fbref_name']], how='left', left_on='team_id', right_on='fbref')
players = players.groupby(['id', 'name'], as_index=False)['minutes'].sum()
players = players[players['minutes']>=500]
players = players.merge(translationDF.loc[:,['fbref', 'transfermarkt']], how='left', left_on='id', right_on='fbref')
missing_players = players[players['transfermarkt'].isnull()]
missing_players = missing_players.merge(player_teams.loc[:,['id', 'fbref_name']], how='left', on='id')


missing_players.to_csv(outputFolder + 'missing_players.txt', index=False)
