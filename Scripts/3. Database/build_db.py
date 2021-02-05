#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Dec 4 2020
#Last updated  Mon Feb 1 2021

#@author: ishepher

#Sources:
    #fbref
    #https://www.sqlitetutorial.net/sqlite-python/creating-database/#:~:text=To%20create%20a%20database%2C%20first,c%3A%5Csqlite%5Cdb%20folder
    #https://likegeeks.com/python-sqlite3-tutorial/#:~:text=will%20return%20zero.-,List%20tables,SQLite3%2C%20which%20stores%20all%20tables
#Input: csvs of data
#Output: SQLite db
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
import numpy as np
import json
import datetime as dt
import glob
import sqlite3
from sqlite3 import Error

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
currentFolder = rootFolder + '/Data/3. Current/'
updatedFolder = rootFolder + '/Data/2. Update/'
fbrefCurFolder = currentFolder + '2. Cleaned/fbref/'
transfermarkCurFolder= currentFolder + '2. Cleaned/transfermarkt/'
fbrefUpFolder = updatedFolder + '2. Cleaned/fbref/'
transfermarkUpFolder= updatedFolder + '2. Cleaned/transfermarkt/'
flatFolder = rootFolder + '/Data/Flat/'
logosFolder = rootFolder + '/Club Logos/'
path = rootFolder + '/db/soccer.db'
outputFolder = currentFolder + '3. Database/'

# Import data
# flat
df_player_translation = pd.read_csv(flatFolder + 'player_translation.txt')
df_team_translation = pd.read_csv(flatFolder + 'team_translation.csv')
with open(flatFolder + 'team_colors.json', encoding='utf-8') as f:
    colors_json = json.load(f)

# fbref (current)
cur_df_meta_stg = pd.read_csv(fbrefCurFolder + 'metadata.csv')
cur_df_officials_stg = pd.read_csv(fbrefCurFolder + 'officials.csv')
cur_df_formations_stg = pd.read_csv(fbrefCurFolder + 'formations.csv')
cur_df_squads_stg = pd.read_csv(fbrefCurFolder + 'squads.csv')
cur_df_match_stats_stg = pd.read_csv(fbrefCurFolder + 'match_stats.csv')
cur_df_player_stats_stg = pd.read_csv(fbrefCurFolder + 'player_stats.csv')
cur_df_player_passing_stats_stg = pd.read_csv(fbrefCurFolder + 'player_passing_stats.csv')
cur_df_player_passing_type_stats_stg = pd.read_csv(fbrefCurFolder + 'player_passing_type_stats.csv')
cur_df_player_defense_stats_stg = pd.read_csv(fbrefCurFolder + 'player_defense_stats.csv')
cur_df_player_possession_stats_stg = pd.read_csv(fbrefCurFolder + 'player_possession_stats.csv')
cur_df_player_misc_stats_stg = pd.read_csv(fbrefCurFolder + 'player_misc_stats.csv')
cur_df_keeper_stats_stg = pd.read_csv(fbrefCurFolder + 'keeper_stats.csv')
# fbref (updated)
up_df_meta_stg = pd.read_csv(fbrefUpFolder + 'metadata.csv')
up_df_officials_stg = pd.read_csv(fbrefUpFolder + 'officials.csv')
up_df_formations_stg = pd.read_csv(fbrefUpFolder + 'formations.csv')
up_df_squads_stg = pd.read_csv(fbrefUpFolder + 'squads.csv')
up_df_match_stats_stg = pd.read_csv(fbrefUpFolder + 'match_stats.csv')
up_df_player_stats_stg = pd.read_csv(fbrefUpFolder + 'player_stats.csv')
up_df_player_passing_stats_stg = pd.read_csv(fbrefUpFolder + 'player_passing_stats.csv')
up_df_player_passing_type_stats_stg = pd.read_csv(fbrefUpFolder + 'player_passing_type_stats.csv')
up_df_player_defense_stats_stg = pd.read_csv(fbrefUpFolder + 'player_defense_stats.csv')
up_df_player_possession_stats_stg = pd.read_csv(fbrefUpFolder + 'player_possession_stats.csv')
up_df_player_misc_stats_stg = pd.read_csv(fbrefUpFolder + 'player_misc_stats.csv')
up_df_keeper_stats_stg = pd.read_csv(fbrefUpFolder + 'keeper_stats.csv')

# transfermarkt (current)
cur_df_player_metadata_stg = pd.read_csv(transfermarkCurFolder + 'player_metadata.csv')
cur_df_player_mv_history_stg = pd.read_csv(transfermarkCurFolder + 'player_mv_history.csv')
cur_df_player_transfer_history_stg = pd.read_csv(transfermarkCurFolder + 'player_transfer_history.csv')
# transfermarkt (updated)
up_df_player_metadata_stg = pd.read_csv(transfermarkUpFolder + 'player_metadata.csv')
up_df_player_mv_history_stg = pd.read_csv(transfermarkUpFolder + 'player_mv_history.csv')
up_df_player_transfer_history_stg = pd.read_csv(transfermarkUpFolder + 'player_transfer_history.csv')

# images
all_images = [os.path.basename(x) for x in glob.glob(logosFolder + '*.png')]
logo_names = [str(i).replace( '.png', '') for i in all_images]

# Append Data
# fbref
df_meta_stg = pd.concat([cur_df_meta_stg.iloc[:,1:],up_df_meta_stg])
df_officials_stg = pd.concat([cur_df_officials_stg.iloc[:,1:],up_df_officials_stg])
df_formations_stg = pd.concat([cur_df_formations_stg.iloc[:,1:],up_df_formations_stg])
df_squads_stg = pd.concat([cur_df_squads_stg.iloc[:,1:],up_df_squads_stg])
df_match_stats_stg = pd.concat([cur_df_match_stats_stg.iloc[:,1:],up_df_match_stats_stg])
df_player_stats_stg = pd.concat([cur_df_player_stats_stg.iloc[:,1:],up_df_player_stats_stg])
df_player_passing_stats_stg = pd.concat([cur_df_player_passing_stats_stg.iloc[:,1:],up_df_player_passing_stats_stg])
df_player_passing_type_stats_stg = pd.concat([cur_df_player_passing_type_stats_stg.iloc[:,1:],up_df_player_passing_type_stats_stg])
df_player_defense_stats_stg = pd.concat([cur_df_player_defense_stats_stg.iloc[:,1:],up_df_player_defense_stats_stg])
df_player_possession_stats_stg = pd.concat([cur_df_player_possession_stats_stg.iloc[:,1:],up_df_player_possession_stats_stg])
df_player_misc_stats_stg = pd.concat([cur_df_player_misc_stats_stg.iloc[:,1:],up_df_player_misc_stats_stg])
df_keeper_stats_stg = pd.concat([cur_df_keeper_stats_stg.iloc[:,1:],up_df_keeper_stats_stg])

# transfermark
df_player_metadata_stg = pd.concat([cur_df_player_metadata_stg, up_df_player_metadata_stg])
df_player_mv_history_stg = pd.concat([cur_df_player_mv_history_stg, up_df_player_mv_history_stg])
df_player_transfer_history_stg = pd.concat([cur_df_player_transfer_history_stg, up_df_player_transfer_history_stg])


# Drop extra files
del cur_df_meta_stg, cur_df_officials_stg, cur_df_formations_stg, cur_df_squads_stg, \
    cur_df_match_stats_stg, cur_df_player_stats_stg, cur_df_player_passing_stats_stg, \
    cur_df_player_passing_type_stats_stg, cur_df_player_defense_stats_stg,  \
    cur_df_player_possession_stats_stg, cur_df_player_misc_stats_stg, cur_df_keeper_stats_stg, \
    up_df_meta_stg, up_df_officials_stg, up_df_formations_stg, up_df_squads_stg, \
    up_df_match_stats_stg, up_df_player_stats_stg, up_df_player_passing_stats_stg, \
    up_df_player_passing_type_stats_stg, up_df_player_defense_stats_stg,  \
    up_df_player_possession_stats_stg, up_df_player_misc_stats_stg, up_df_keeper_stats_stg, \
    cur_df_player_metadata_stg, cur_df_player_mv_history_stg, cur_df_player_transfer_history_stg, \
    up_df_player_metadata_stg, up_df_player_mv_history_stg, up_df_player_transfer_history_stg



#~~~~~PREP DATA~~~~~

# Convert json
def extract_colors(json):
    
    teamLong = []
    teamShort = []
    colorPrimary = []
    colorSecondary = []
    colorTertiary = []
        
    for i in range(0,len(json)):
        mydict = json[i]
        teamcolors = mydict.get('TeamColours')
        teamShort.append(mydict.get('TeamShort'))
        teamLong.append(mydict.get('TeamLong'))
        colorPrimary.append(teamcolors[0] if len(teamcolors) > 0 else np.nan)
        colorSecondary.append(teamcolors[1] if len(teamcolors) > 1 else np.nan)
        colorTertiary.append(teamcolors[2] if len(teamcolors) > 2 else np.nan)
        
    df = pd.DataFrame(zip(teamShort, teamLong, colorPrimary, colorSecondary, colorTertiary),
                            columns = ['short_name', 'long_name', 'primary_color', 'secondary_color', 'alternate_color'])
    
    return df

df_colors_stg = extract_colors(colors_json)

# Reset index
df_meta_stg = df_meta_stg.reset_index(drop=True).reset_index()
df_officials_stg = df_officials_stg.reset_index(drop=True).reset_index()
df_formations_stg = df_formations_stg.reset_index(drop=True).reset_index()
df_squads_stg = df_squads_stg.reset_index(drop=True).reset_index()
df_match_stats_stg = df_match_stats_stg.reset_index(drop=True).reset_index()
df_player_stats_stg = df_player_stats_stg.reset_index(drop=True).reset_index()
df_player_passing_stats_stg = df_player_passing_stats_stg.reset_index(drop=True).reset_index()
df_player_passing_type_stats_stg = df_player_passing_type_stats_stg.reset_index(drop=True).reset_index()
df_player_defense_stats_stg = df_player_defense_stats_stg.reset_index(drop=True).reset_index()
df_player_possession_stats_stg = df_player_possession_stats_stg.reset_index(drop=True).reset_index()
df_player_misc_stats_stg = df_player_misc_stats_stg.reset_index(drop=True).reset_index()
df_keeper_stats_stg = df_keeper_stats_stg.reset_index(drop=True).reset_index()


# Primary Keys
df_meta_stg = df_meta_stg.rename(columns={df_meta_stg.columns[0]: "match_key"})
df_officials_stg = df_officials_stg.rename(columns={df_officials_stg.columns[0]: "match_key"})
df_formations_stg = df_formations_stg.rename(columns={df_formations_stg.columns[0]: "match_key"})
df_squads_stg = df_squads_stg.rename(columns={df_squads_stg.columns[0]: "squads_key"})
df_match_stats_stg = df_match_stats_stg.rename(columns={df_match_stats_stg.columns[0]: "match_stats_key"})
df_player_stats_stg = df_player_stats_stg.rename(columns={df_player_stats_stg.columns[0]: "player_match_key"})
df_player_passing_stats_stg = df_player_passing_stats_stg.rename(columns={df_player_passing_stats_stg.columns[0]: "player_match_key"})
df_player_passing_type_stats_stg = df_player_passing_type_stats_stg.rename(columns={df_player_passing_type_stats_stg.columns[0]: "player_match_key"})
df_player_defense_stats_stg = df_player_defense_stats_stg.rename(columns={df_player_defense_stats_stg.columns[0]: "player_match_key"})
df_player_possession_stats_stg = df_player_possession_stats_stg.rename(columns={df_player_possession_stats_stg.columns[0]: "player_match_key"})
df_player_misc_stats_stg = df_player_misc_stats_stg.rename(columns={df_player_misc_stats_stg.columns[0]: "player_match_key"})
df_keeper_stats_stg = df_keeper_stats_stg.rename(columns={df_keeper_stats_stg.columns[0]: "keeper_match_key"})
df_player_metadata_stg = df_player_metadata_stg.reset_index().rename(columns={'index' : 'player_key'})

# Pass foreign keys, change headers, and add calculations

# teams
df_team_stg = df_team_translation.copy()
df_team_stg = df_team_stg.merge(df_colors_stg, how='left', left_on='fcpython_name', right_on='short_name').drop(columns=['short_name'])
df_team = df_team_stg.copy()

# meta (fbref)
df_meta_stg['league'] = df_meta_stg['url'].str.split('-').str[-2:]
df_meta_stg['league'] = df_meta_stg['league'].str.join(' ')
df_meta_stg['league'] = np.where(df_meta_stg['league'].str.contains('Bundesliga'), 'Bundesliga', df_meta_stg['league'])
df_meta_stg['date'] = pd.to_datetime(df_meta_stg['date']).dt.date
df_meta_stg['season'] = np.where(df_meta_stg['date']<dt.date(2018,7,1), '17/18',
                                     np.where(df_meta_stg['date']<dt.date(2019,7,1), '18/19',
                                              np.where((df_meta_stg['date']<dt.date(2020,9,1)) & (df_meta_stg['league'] != 'Ligue 1'), '19/20', 
                                                       np.where(df_meta_stg['date']<dt.date(2020,9,1), '19/20', 
                                                            np.where(df_meta_stg['date']<dt.date(2021,7,1), '20/21', np.nan)))))

df_meta_stg = df_meta_stg.loc[:,['match_key', 'id', 'url', 'date', 'kickoff', 'venue', 'attendance',
                                 'league', 'season', 'id_x', 'team_x', 'id_y', 'team_y', 'manager_x', 'manager_y',
                                 'captain_x', 'captain_id_x', 'captain_y', 'captain_id_y', 'score_x',
                                 'score_y', 'xg_x', 'xg_y']]

df_meta = df_meta_stg.copy()

# officials
df_officials = df_officials_stg.copy()

# formations
df_formations = df_formations_stg.copy()

# squads
df_squads_stg = df_squads_stg.rename(columns={'id' : 'player_id',
                                              'url' : 'player_url',
                                              'name' : 'player_name'})
df_squads_stg = df_squads_stg.merge(df_meta_stg.loc[:,['match_key', 'id']], how='inner', left_on='match_id', right_on='id')
df_squads_stg = df_squads_stg.loc[:,['squads_key', 'match_key', 'match_id', 'team_id', 'player_id', 'player_url', 'player_name']]
df_squads_stg['player_name'] = df_squads_stg['player_name'].str.replace("-", " ")
df_squads = df_squads_stg.copy()

# match stats
df_match_stats = df_match_stats_stg.copy()

# player stats
df_player_stats_stg = df_player_stats_stg.rename(columns={'id' : 'player_id',
                                                          'name' : 'player_name'})
df_player_stats_stg = df_player_stats_stg.merge(df_meta_stg.loc[:,['match_key', 'id']], how='inner', left_on='match_id', right_on='id')
df_player_stats_stg['player_name'] = df_player_stats_stg['player_name'].str.replace("-", " ")
df_player_stats_stg[['pos_1', 'pos_2', 'pos_3', 'pos_4', 'pos_5']] = pd.DataFrame([x.split(',') for x in df_player_stats_stg['position'].tolist()])
df_player_stats_stg['nation'] = df_player_stats_stg['nation'].str.split(' ').str[1]
df_player_stats_stg = df_player_stats_stg.loc[:,['player_match_key', 'match_key', 'match_id', 'team_id', 
                                                 'player_id', 'player_name', 'shirtnumber', 'nation', 'age', 
                                                 'position', 'pos_1', 'pos_2', 'pos_3', 'pos_4', 'pos_5',
                                                 'minutes', 'goals', 'assists', 'pk', 'pk_attempted', 
                                                 'shots', 'shots_on_target', 'card_yellow', 'card_red',
                                                 'touches', 'pressures', 'tackles', 'interceptions', 'blocks',
                                                 'xG', 'npxG', 'xA', 'shot_creating_actions', 'goal_creating_actions',
                                                 'passes_completed', 'passes_attempted', 'pass_progressive_distance',
                                                 'carries', 'dribble_progressive_distance', 'dribble_success', 'dribble_attempt']]
df_player_stats = df_player_stats_stg.copy()

# player passing stats
df_player_passing_stats_stg = df_player_passing_stats_stg.rename(columns={'id' : 'player_id'})
df_player_passing_stats = df_player_passing_stats_stg.copy()

# player passing type stats
df_player_passing_type_stats_stg = df_player_passing_type_stats_stg.rename(columns={'id' : 'player_id'})
df_player_passing_type_stats = df_player_passing_type_stats_stg.copy()

# player defense stats
df_player_defense_stats_stg = df_player_defense_stats_stg.rename(columns={'id' : 'player_id'})
df_player_defense_stats = df_player_defense_stats_stg.copy()

# player possession stats
df_player_possession_stats_stg = df_player_possession_stats_stg.rename(columns={'id' : 'player_id'})
df_player_possession_stats = df_player_possession_stats_stg.copy()

# player misc stats
df_player_misc_stats_stg = df_player_misc_stats_stg.rename(columns={'id' : 'player_id'})
df_player_misc_stats = df_player_misc_stats_stg.copy()

# keeper stats
df_keeper_stats_stg = df_keeper_stats_stg.rename(columns={'id' : 'player_id',
                                                          'name' : 'player_name'})
df_keeper_stats_stg = df_keeper_stats_stg.merge(df_meta_stg.loc[:,['match_key', 'id']], how='inner', left_on='match_id', right_on='id')
df_keeper_stats_stg['nation'] = df_keeper_stats_stg['nation'].str.split(' ').str[1]
df_keeper_stats_stg = df_keeper_stats_stg.loc[:,['keeper_match_key', 'match_key', 'match_id', 'team_id', 
                                                 'player_id', 'player_name', 'nation', 'age', 
                                                 'minutes', 'shots_against', 'goals_allowed', 'saves',
                                                 'xGA', 'launched_completed', 'launched_attempted', 'passes_attempted',
                                                 'throws_attempted', 'passes_avg_length', 'gk_attempted',
                                                 'gk_avg_length', 'crosses_faced', 'crosses_stopped',
                                                 'defensive_actions', 'defensive_actions_avg_distance']]
df_keeper_stats = df_keeper_stats_stg.copy()

# meta (transfermarkt)
df_player_metadata_stg['born'] = pd.to_datetime(df_player_metadata_stg['born']).dt.date
df_player_metadata_stg['joined'] = pd.to_datetime(df_player_metadata_stg['joined']).dt.date
df_player_metadata_stg['contracted'] = pd.to_datetime(df_player_metadata_stg['contracted']).dt.date
df_player_metadata_stg['update'] = pd.to_datetime(df_player_metadata_stg['update']).dt.date
df_player_metadata = df_player_metadata_stg.copy()

# mv history
df_player_mv_history_stg['date'] = pd.to_datetime(df_player_mv_history_stg['date']).dt.date
df_player_mv_history_stg = df_player_mv_history_stg.merge(df_player_metadata_stg.loc[:,['player_key', 'id']], how='left', on='id')
df_player_mv_history_stg = df_player_mv_history_stg.loc[:,['player_key', 'id', 'date', 'team', 'value']]
df_player_mv_history = df_player_mv_history_stg.copy()

# transfer history
df_player_transfer_history_stg['date'] = pd.to_datetime(df_player_transfer_history_stg['date']).dt.date
df_player_transfer_history_stg = df_player_transfer_history_stg.merge(df_player_metadata_stg.loc[:,['player_key', 'id']], how='left', on='id')
df_player_transfer_history_stg = df_player_transfer_history_stg.loc[:,['player_key', 'id', 'date', 'left', 'joined',
                                                                       'value', 'fee', 'future', 'loan', 'loan_fee', 'free']]
df_player_transfer_history = df_player_transfer_history_stg.copy()


# player (custom table)
df_player_stg = df_player_stats_stg.loc[:,['player_id', 'player_name', 'position']]
df_player_stg['FWD/AM'] = np.where(df_player_stg['position'].str.contains('FW|LW|RW|AM'), 1, 0)
df_player_stg['WM'] = np.where(df_player_stg['position'].str.contains('LM|RM'), 1, 0)
df_player_stg['CM/DM'] = np.where(df_player_stg['position'].str.contains('CM|DM|MF'), 1, 0)
df_player_stg['FB'] = np.where(df_player_stg['position'].str.contains('LB|RB|WB'), 1, 0)
df_player_stg['CB'] = np.where(df_player_stg['position'].str.contains('CB|DF'), 1, 0)
df_player_stg['GK'] = np.where(df_player_stg['position'].str.contains('GK'), 1, 0)
df_player_stg = df_player_stg.groupby(['player_id', 'player_name']).sum()
df_player_stg['pos_group'] = df_player_stg.idxmax(axis=1)
df_player_stg = df_player_stg.loc[:,['pos_group']]
df_player_stg = df_player_stg.reset_index()

df_player_stg = df_player_stg.merge(df_player_translation.loc[:,['fbref', 'transfermarkt']],
                                    how='left', left_on='player_id', right_on='fbref')
df_player_stg = df_player_stg.merge(df_player_metadata_stg, how='left', left_on='transfermarkt', right_on='id')
df_player_stg = df_player_stg.loc[:,['player_id', 'transfermarkt', 'player_name', 'pos_group',
                                     'born', 'birth_place', 'nationality', 'height',
                                     'club', 'joined', 'contracted', 'mv', 'update']]
df_player_stg = df_player_stg.rename(columns={'player_id' : 'fbref'})
df_player_stg = df_player_stg.sort_values('player_name')
df_player = df_player_stg.copy()


# player tenure (custom table)
df_player_tenure_stg = df_player_transfer_history_stg.loc[:,['id', 'date', 'left', 'joined']]
df_player_tenure_stg = df_player_tenure_stg[df_player_tenure_stg['date'] <= dt.date.today()]
youth_strings = ['II', 'Youth', 'Academy', 'Academia', 'U15', 'U16', 'U17', 'U18', 'U19', 'U20', 'U21', 'U23', 'B \(liq.\)', 'C \(liq.\)']
df_player_tenure_stg['youth'] = np.where((df_player_tenure_stg['left'].str.contains('|'.join(youth_strings))) |
                                         (df_player_tenure_stg['left'].str.endswith((' B',' C'))) , 'Y', 'N')
df_player_tenure_stg['arrived'] = np.where(df_player_tenure_stg['id']==df_player_tenure_stg['id'].shift(), df_player_tenure_stg['date'].shift(), np.nan)
df_player_tenure_stg = df_player_tenure_stg.merge(df_player_stg.loc[:,['transfermarkt', 'born']], 
                                                  how='left', left_on='id', right_on='transfermarkt')
df_player_tenure_stg['arrived'] = df_player_tenure_stg['arrived'].fillna(df_player_tenure_stg['born'])
df_player_tenure_stg_ = df_player_tenure_stg.loc[:,['id', 'joined', 'date']]
df_player_tenure_stg_ = df_player_tenure_stg_.drop_duplicates(subset=['id'], keep='last')
df_player_tenure_stg_['youth'] = np.where((df_player_tenure_stg_['joined'].str.contains('|'.join(youth_strings))) |
                                         (df_player_tenure_stg_['joined'].str.endswith((' B',' C'))) , 'Y', 'N')
df_player_tenure_stg_ = df_player_tenure_stg_.rename(columns={'joined' : 'team',
                                                              'date' : 'arrived'})
df_player_tenure_stg = df_player_tenure_stg.loc[:,['id', 'left', 'youth', 'arrived', 'date']]
df_player_tenure_stg = df_player_tenure_stg.rename(columns={'left' : 'team',
                                                            'date' : 'departed'})
df_player_tenure_stg = pd.concat([df_player_tenure_stg, df_player_tenure_stg_]).sort_values(['id', 'arrived'])
df_player_tenure = df_player_tenure_stg.copy()


# drop extra variables 
del colors_json, df_colors_stg, df_team_stg, \
    df_meta_stg, df_officials_stg, df_formations_stg, df_squads_stg, df_match_stats_stg, \
    df_player_stats_stg, df_player_passing_stats_stg, df_player_passing_type_stats_stg, df_player_defense_stats_stg, \
    df_player_possession_stats_stg, df_player_misc_stats_stg, df_keeper_stats_stg, \
    df_player_metadata_stg, df_player_mv_history_stg, df_player_transfer_history_stg, df_player_tenure_stg, df_player_tenure_stg_



#~~~~~BUILD DATABASE~~~~~

# Data tables and views
def create_connection(db_file):
    
    # create a database connection to a SQLite database
    con = None
    try:
        con = sqlite3.connect(db_file)
        # print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if con:
            con.close()


if __name__ == '__main__':
    create_connection(path)
    


def create_table(df, tableName):
    con = sqlite3.connect(path)    
    
    df.to_sql(tableName, con, if_exists='replace')
    con.close()

def create_view(name, sql):
    
    con = sqlite3.connect(path)
    cursorObj = con.cursor()
    
    sql = "CREATE VIEW " + name + " AS " + sql
    cursorObj.execute(sql)
    
    # con.commit
    con.close()

# Blob tables
def create_logo_table(tableName, sql):
    
    con = sqlite3.connect(path)
    cursorObj = con.cursor()
    
    try:
        cursorObj.execute(sql)
    except:
    
        dropTable = """DROP TABLE """ + tableName
        cursorObj.execute(dropTable)
        cursorObj.execute(sql)
        print('table dropped')
        
    con.close()    


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def insertBLOB(team_id, team_name, logo):
    
    try:
        con = sqlite3.connect(path)
        cursorObj = con.cursor()
        sqlite_insert_blob_query = """ INSERT INTO club_logos_dim
                                  (id, logo) VALUES (?, ?)"""

        teamLogo = convertToBinaryData(logo)
        # Convert data into tuple format
        data_tuple = (team_id, teamLogo)
        cursorObj.execute(sqlite_insert_blob_query, data_tuple)
        con.commit()
        print(team_name + " inserted")
        cursorObj.close()

    except sqlite3.Error as error:
        print("Failed to insert " + team_name, error)
     
    con.close()
 

# Tables
create_table(df_player_translation, 'player_translation')
create_table(df_team_translation, 'team_translation')
create_table(df_team, 'team_dim')
create_table(df_meta, 'match_dim')
create_table(df_officials, 'official_dim')
create_table(df_formations, 'formation_dim')
create_table(df_squads, 'matchday_squad_fact')
create_table(df_match_stats, 'matchday_stats_fact')
create_table(df_player_stats, 'player_match_stats_fact')
create_table(df_player_passing_stats, 'player_passing_match_stats_fact')
create_table(df_player_passing_type_stats, 'player_passing_type_match_stats_fact')
create_table(df_player_defense_stats, 'player_defense_match_stats_fact')
create_table(df_player_possession_stats, 'player_possession_match_stats_fact')
create_table(df_player_misc_stats, 'player_misc_match_stats_fact')
create_table(df_keeper_stats, 'keeper_match_stats_fact')
create_table(df_player, 'player_dim')
create_table(df_player_metadata, 'trans_player_dim')
create_table(df_player_mv_history, 'trans_mv_fact')
create_table(df_player_transfer_history, 'trans_transfer_fact')
create_table(df_player_tenure, 'trans_player_tenure_fact')


# Views
# sql
formationSql = """
SELECT f.match_key, f.match_id, m.id_x "team_id", f.formation_x "formation" FROM formation_dim f LEFT JOIN match_dim m ON f.match_key = m.match_key
UNION ALL
SELECT f.match_key, f.match_id, m.id_y "team_id", f.formation_y "formation" FROM formation_dim f LEFT JOIN match_dim m ON f.match_key = m.match_key
"""
match_statsSql = """
SELECT
	s.match_stats_key, s.match_id, m.id_x "team_id", s.possession_x "possession", s.fouls_x "fouls", s.corners_x "corners",	s.crosses_x "crosses",
    s.touches_x "touches", s.tackles_x "tackles", s.interceptions_x "interceptions", s.aerials_won_x "aerials won", s.clearances_x "clearances",
	s.offsides_x "offsides", s.goal_kicks_x "goal kicks", s.throw_ins_x "throw ins", s.long_balls_x "long balls" 
FROM matchday_stats_fact s LEFT JOIN match_dim m ON s.match_id = m.id
UNION ALL
SELECT
	s.match_stats_key, s.match_id, m.id_y "team_id", s.possession_y "possession", s.fouls_y "fouls", s.corners_y "corners", s.crosses_y "crosses",
	s.touches_y "touches", s.tackles_y "tackles", s.interceptions_y "interceptions", s.aerials_won_y "aerials won", s.clearances_y "clearances",
	s.offsides_y "offsides", s.goal_kicks_y "goal kicks", s.throw_ins_y "throw ins", s.long_balls_y "long balls"
FROM matchday_stats_fact s LEFT JOIN match_dim m ON s.match_id = m.id
"""
player_statsSql = """
SELECT
    s.match_key, s.team_id, s.player_id, s.position, s.minutes, s.goals, s.assists, s.pk, s.pk_attempted, s.xG, s.npxG, s.xA, 
    s.shot_creating_actions, s.goal_creating_actions, s.shots, s.shots_on_target, s.passes_attempted, s.passes_completed, p.total_distance,
    s.pass_progressive_distance, p.short_completed, p.short_attempted, p.medium_completed, p.medium_attempted, p.long_completed, p.long_attempted,
    p.key_passes, p.into_final_third, p.into_pen_area, p.crosses_into_pen, p.progressive, pt.live, pt.dead, pt.free_kick, pt.through_balls,
    pt.under_pressure, pt.switches, pt.crosses, pt.corner_kicks, pt.corner_inswing, pt.corner_outswing, pt.corner_straight, 
    pt.height_ground, pt.height_low, pt.height_high, pt.body_left, pt.body_right, pt.body_head, pt.body_throw_in, pt.body_other, 
    pt.offsides offside_passes, pt.out_of_bounds, pt.intercepted, pt.blocked, po.passes_targeted, po.passes_received, po.miscontrols, po.dispossessed,
    s.touches, po.touches_defensive_pen, po.touches_defensive_third, po.touches_middle_third, po.touches_attacking_third, po.touches_attacking_pen, 
    po.touches_live, s.carries, po.carry_distance, po.carry_progressive_distance, s.dribble_progressive_distance, s.dribble_success, s.dribble_attempt,
    po.dribbles_past, po.dribble_megs, s.tackles, m.tackles_won, d.tackles_defensive_third, d.tackles_middle_third, d.tackles_attacking_third,
    d.dribble_tackles, d.dribble_tackles_attempted, d.dribbled_past, s.pressures, d.pressures_successful, d.pressures_defensive_third, d.pressures_middle_third,
    d.pressures_attacking_third, s.blocks, d.blocked_shots, d.blocked_shots_on_target, d.blocked_passes, s.interceptions, d.clearances, d.errors, m.recoveries,
    m.aerials_lost, m.aerials_won, m.cards_yellow, m.cards_red, m.cards_second_yellow, m.fouls, m.fouled, m.offsides, m.pk_won, m.pk_con, m.own_goals
FROM player_match_stats_fact s
LEFT JOIN player_passing_match_stats_fact p ON s.player_match_key = p.player_match_key
LEFT JOIN player_passing_type_match_stats_fact pt ON s.player_match_key = pt.player_match_key
LEFT JOIN player_defense_match_stats_fact d ON s.player_match_key = d.player_match_key
LEFT JOIN player_possession_match_stats_fact po ON s.player_match_key = po.player_match_key
LEFT JOIN player_misc_match_stats_fact m ON s.player_match_key = m.player_match_key
"""


# create views
# create_view('v_formation_dim', formationSql)
# create_view('v_match_stats_fact', match_statsSql)
# create_view('v_player_match_stats_fact', player_statsSql)

# Logos

logos_sql = """CREATE TABLE "club_logos_dim" ("id" TEXT, "logo" BLOB)"""
# create_logo_table('club_logos_dim', logos_sql)

# for i in range(0,len(all_images)):
#     team_ = logo_names[i]
#     id_ = df_team_translation[df_team_translation['fbref_name']==team_].iloc[0,0]
    
#     insertBLOB(id_, team_, logosFolder + all_images[i])


#~~~~~OUPUT DATABASE COPIES~~~~~

# other
df_player_translation.to_csv(outputFolder + 'player_translation.csv')
df_team_translation.to_csv(outputFolder + 'team_translation.csv')
df_team.to_csv(outputFolder + 'team_dim.csv')
df_player.to_csv(outputFolder + 'player_dim.csv')

# fbref
df_meta.to_csv(outputFolder + 'match_dim.csv')
df_officials.to_csv(outputFolder + 'official_dim.csv')
df_formations.to_csv(outputFolder + 'formation_dim.csv')
df_squads.to_csv(outputFolder + 'matchday_squad_fact.csv')
df_match_stats.to_csv(outputFolder + 'matchday_stats_fact.csv')
df_player_stats.to_csv(outputFolder + 'player_match_stats_fact.csv')
df_player_passing_stats.to_csv(outputFolder + 'player_passing_match_stats_fact.csv')
df_player_passing_type_stats.to_csv(outputFolder + 'player_passing_type_match_stats_fact.csv')
df_player_defense_stats.to_csv(outputFolder + 'player_defense_match_stats_fact.csv')
df_player_possession_stats.to_csv(outputFolder + 'player_possession_match_stats_fact.csv')
df_player_misc_stats.to_csv(outputFolder + 'player_misc_match_stats_fact.csv')
df_keeper_stats.to_csv(outputFolder + 'keeper_match_stats_fact.csv')

# transfermarkt
df_player_metadata.to_csv(outputFolder + 'trans_player_dim.csv')
df_player_mv_history.to_csv(outputFolder + 'trans_mv_fact.csv')
df_player_transfer_history.to_csv(outputFolder + 'trans_transfer_fact.csv')
df_player_tenure.to_csv(outputFolder + 'trans_player_tenure_fact.csv')