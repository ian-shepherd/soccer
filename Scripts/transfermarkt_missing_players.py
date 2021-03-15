#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Fri Jan 29 2021
#Last updated Tue Mar 9 2021

#@author: ishepher

#Sources:
    #fbref
#Input: csv of match stats
#Output: csv of players to add to translation table
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
rootFolder = os.path.dirname(os.path.dirname(__file__))
flatFolder = rootFolder + '/Data/Flat/'
dbFolder = rootFolder + '/Data/Database/'
updatedFolder = rootFolder + '/Data/Update/'


# Import data
translationDF = pd.read_csv(flatFolder + 'player_translation.txt')
teamsDF = pd.read_csv(flatFolder + 'team_translation.csv')
dbDF = pd.read_csv(dbFolder + 'player_match_stats_fact.csv')
updateDF = pd.read_csv(updatedFolder + 'player_stats.csv')


# Subset data
dbDF = dbDF.loc[:,['player_id', 'player_name', 'team_id', 'minutes']].rename(columns={'player_id' : 'id',
                                                                                      'player_name' : 'name'})
updateDF = updateDF.loc[:,['id', 'name', 'team_id', 'minutes']]

dbDF = dbDF.astype(str)
updateDF = updateDF.astype(str)


# Find missing players
players = pd.concat([dbDF, updateDF])
players['minutes'] = players['minutes'].astype(float)
player_teams = players.drop_duplicates(subset=['id'], keep='last')
player_teams = player_teams.loc[:,['id', 'team_id']].merge(teamsDF.loc[:,['fbref', 'fbref_name']], how='left', left_on='team_id', right_on='fbref')
players = players.groupby(['id', 'name'], as_index=False)['minutes'].sum()
players = players[players['minutes']>=500]
players = players.merge(translationDF.loc[:,['fbref', 'transfermarkt']], how='left', left_on='id', right_on='fbref')
missing_players = players[players['transfermarkt'].isnull()]
missing_players = missing_players.merge(player_teams.loc[:,['id', 'fbref_name']], how='left', on='id')


missing_players.to_csv(updatedFolder + 'missing_players.txt', index=False)
