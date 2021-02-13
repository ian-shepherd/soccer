#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Oct 24  2020
#Last updated Wed Feb 10 2021

#@author: ishepher

#Sources:
    #fbref
#Input: csv of matches urls for big 5 leagues (2017-2020) and CL/Europa (2018-2020)
#Output: pickle of match stats
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
import pickle
import pandas as pd
import numpy as np
import time
import random

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
dataFolder = rootFolder + '/Data/'
inputFolder = dataFolder + '2. Update/Flat/'
dbFolder = dataFolder + '3. Current/3. Database/'
outputFolder = dataFolder + '2. Update/1. Raw/fbref/'

# Load data
match_urls = pd.read_csv(inputFolder + 'match_urls.csv')
current_matches = pd.read_csv(dbFolder + 'match_dim.csv')

# Filter matches in dataset
match_urls = match_urls.merge(current_matches.loc[:,['url']], how='left', left_on='urls', right_on='url')
match_urls = match_urls[match_urls['url'].isnull()]
    
# Tell webpage human browser
headers = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}


#~~~~~SCRAPE DATA~~~~~

# Master function match_data calls metadata, lineups, team_stats, and player_stats functions
# creates a tuple for each match

def metadata(pageSoup, url):
    
    
    scorebox = pageSoup.find('div', {'class' : 'scorebox'})
    teams = scorebox.find_all('div', {'itemprop' : 'performer'})
    
    id_x = teams[0].find('a', href=True)['href'].split('/')[3]
    id_y = teams[1].find('a', href=True)['href'].split('/')[3]
    team_x = teams[0].find('a', href=True).text
    team_y = teams[1].find('a', href=True).text
    
    scores = pageSoup.find_all('div', {'class' : 'scores'})
    score_x = scores[0].find('div', {'class' : 'score'}).text
    xg_x = scores[0].find('div', {'class' : 'score_xg'}).text
    score_y = scores[1].find('div', {'class' : 'score'}).text
    xg_y = scores[1].find('div', {'class' : 'score_xg'}).text
    
    managers = pageSoup.find_all('div', {'class' : 'datapoint'})
    manager_x = managers[0].text.replace('Manager: ', '')
    manager_y = managers[2].text.replace('Manager: ', '')
    captain_x = managers[1].find('a', href=True)['href']
    captain_y = managers[3].find('a', href=True)['href']

    
    scorebox_meta = pageSoup.find('div', {'class' : 'scorebox_meta'})
    datetime = scorebox_meta.find('span', {'class' : 'venuetime'})
    date = datetime['data-venue-date']
    kickoff = datetime['data-venue-time']
    scorebox_meta_ = scorebox_meta.find_all('div')
    if scorebox_meta_[4].text.startswith('Attendance:'):
        attendance = scorebox_meta_[4].text
        venue = scorebox_meta_[5].text.replace('Venue: ', '')
        officials = scorebox_meta_[6].find_all('small')[1].text.split('\xa0· ')
    else:
        attendance = None
        venue = scorebox_meta_[4].text.replace('Venue: ', '')
        officials = scorebox_meta_[5].find_all('small')[1].text.split('\xa0· ')
    
    
    mydict = {'url' : url,
              'id_x' : id_x,
              'id_y' : id_y,
              'team_x' : team_x,
              'team_y' : team_y,
              'score_x' : score_x,
              'score_y' : score_y,
              'xg_x' : xg_x,
              'xg_y' : xg_y,
              'manager_x' : manager_x,
              'manager_y' : manager_y,
              'captain_x' : captain_x,
              'captain_y' : captain_y,
              'date' : date,
              'kickoff' : kickoff,
              'attendance' : attendance,
              'venue' : venue,
              'officials' : officials}
    
    return mydict


def lineups(pageSoup):
    

    lineup = pageSoup.find_all('div', {'class' : 'lineup'})
    lineup_x = lineup[0].find('table').find_all('tr')
    formation_x = lineup_x[0].text
    squad_x = []
    for row in range(1,len(lineup_x)):
        if row != 12:
            squad_x.append(lineup_x[row].find('a', href=True)['href'])
            
    lineup_y = lineup[1].find('table').find_all('tr')
    formation_y = lineup_y[0].text
    squad_y = []
    for row in range(1,len(lineup_y)):
        if row != 12:
            squad_y.append(lineup_y[row].find('a', href=True)['href'])
            
    mydict = {'formation_x' : formation_x,
              'formation_y' : formation_y,
              'squad_x' : squad_x,
              'squad_y' : squad_y}
    
    return mydict


def team_stats(pageSoup):
    
    stats = pageSoup.find('div', {'id' : 'team_stats'})
    statsTable = stats.find('table').find_all('tr')
    possession = statsTable[2].find_all('strong')
    possession_x = possession[0].text
    possession_y = possession[1].text
    
    
    extra = pageSoup.find('div', {'id' : 'team_stats_extra'})
    extraTable = extra.find_all('div')
    fouls_x = extraTable[4].text
    fouls_y = extraTable[6].text
    corners_x = extraTable[7].text
    corners_y = extraTable[9].text
    crosses_x = extraTable[10].text
    crosses_y = extraTable[12].text
    touches_x = extraTable[13].text
    touches_y = extraTable[15].text
    tackles_x = extraTable[20].text
    tackles_y = extraTable[22].text
    interceptions_x = extraTable[23].text
    interceptions_y = extraTable[25].text
    aerials_won_x = extraTable[26].text
    aerials_won_y = extraTable[28].text
    clearances_x = extraTable[29].text
    clearances_y = extraTable[31].text
    offsides_x = extraTable[36].text
    offsides_y = extraTable[38].text
    goal_kicks_x = extraTable[39].text
    goal_kicks_y = extraTable[41].text
    throw_ins_x = extraTable[42].text
    throw_ins_y = extraTable[44].text
    long_balls_x = extraTable[45].text
    long_balls_y = extraTable[47].text
        
    
    mydict = {'possession_x' : possession_x,
              'possession_y' : possession_y,
              'fouls_x' : fouls_x,
              'fouls_y' : fouls_y,
              'corners_x' : corners_x,
              'corners_y' : corners_y,
              'crosses_x' : crosses_x,
              'crosses_y' : crosses_y,
              'touches_x' : touches_x,
              'touches_y' : touches_y,
              'tackles_x' : tackles_x,
              'tackles_y' : tackles_y,
              'interceptions_x' : interceptions_x,
              'interceptions_y' : interceptions_y,
              'aerials_won_x' : aerials_won_x,
              'aerials_won_y' : aerials_won_y,
              'clearances_x' : clearances_x,
              'clearances_y' : clearances_y,
              'offsides_x' : offsides_x,
              'offsides_y' : offsides_y,
              'goal_kicks_x' : goal_kicks_x,
              'goal_kicks_y' : goal_kicks_y,
              'throw_ins_x' : throw_ins_x,
              'throw_ins_y' : throw_ins_y,
              'long_balls_x' : long_balls_x,
              'long_balls_y' : long_balls_y}

    return mydict


def player_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_summary'
    
    stats_players = pageSoup.find('table', {'id' : id_})
    stats_players = stats_players.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_players)-1):
        th = stats_players[row].find('th')
        name = th['data-append-csv']
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_players[row].find_all('td')
        shirtnumber = player_[0].text
        nation = player_[1].text
        position = player_[2].text
        age = player_[3].text
        minutes = player_[4].text
        goals = player_[5].text
        assists = player_[6].text
        pk = player_[7].text
        pk_attempted = player_[8].text
        shots = player_[9].text
        shots_on_target = player_[10].text
        card_yellow = player_[11].text
        card_red = player_[12].text
        touches = player_[13].text
        pressures = player_[14].text
        tackles = player_[15].text
        interceptions = player_[16].text
        blocks = player_[17].text
        xG = player_[18].text
        npxG = player_[19].text
        xA = player_[20].text
        shot_creating_actions = player_[21].text
        goal_creating_actions = player_[22].text
        passes_completed = player_[23].text
        passes_attempted = player_[24].text
        pass_progressive_distance = player_[26].text
        carries = player_[27].text
        dribble_progressive_distance = player_[28].text
        dribble_success = player_[29].text
        dribble_attempt = player_[30].text
        
        mydict = {'player_id' : id_,
                  'name' : name,
                  'shirtnumber' : shirtnumber,
                  'nation' : nation,
                  'position' : position,
                  'age' : age,
                  'minutes' : minutes,
                  'goals' : goals,
                  'assists' : assists,
                  'pk' : pk,
                  'pk_attempted' : pk_attempted,
                  'shots' : shots,
                  'shots_on_target' : shots_on_target,
                  'card_yellow' : card_yellow,
                  'card_red' : card_red,
                  'touches' : touches,
                  'pressures' : pressures,
                  'tackles' : tackles,
                  'interceptions' : interceptions,
                  'blocks' : blocks,
                  'xG' : xG,
                  'npxG' : npxG,
                  'xA' : xA,
                  'shot_creating_actions' : shot_creating_actions,
                  'goal_creating_actions' : goal_creating_actions,
                  'passes_completed' : passes_completed,
                  'passes_attempted' : passes_attempted,
                  'pass_progressive_distance' : pass_progressive_distance,
                  'carries' : carries,
                  'dribble_progressive_distance' : dribble_progressive_distance,
                  'dribble_success' : dribble_success,
                  'dribble_attempt' : dribble_attempt
            }
    
        mylist.append(mydict)
        
    
    return mylist


def passing_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_passing'
    
    stats_passing = pageSoup.find('table', {'id' : id_})
    stats_passing = stats_passing.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_passing)-1):
        th = stats_passing[row].find('th')
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_passing[row].find_all('td')
        cmp = player_[5].text
        att = player_[6].text
        totdist = player_[8].text
        prgdist = player_[9].text
        short_cmp = player_[10].text
        short_att = player_[11].text
        med_cmp = player_[13].text
        med_att = player_[14].text
        long_cmp = player_[16].text
        long_att = player_[17].text
        ast = player_[19].text
        xA = player_[20].text
        key_passes = player_[21].text
        final_third = player_[22].text
        ppa = player_[23].text
        crs_ppa = player_[24].text
        prog = player_[25].text
    
        mydict = {'player_id' : id_,
                  'completed' : cmp,
                  'attempted' : att,
                  'total_distance' : totdist,
                  'progressive_distance' : prgdist,
                  'short_completed' : short_cmp,
                  'short_attempted' : short_att,
                  'medium_completed' : med_cmp,
                  'medium_attempted' : med_att,
                  'long_completed' : long_cmp,
                  'long_attempted' : long_att,
                  'assists' : ast,
                  'xA' : xA,
                  'key_passes' : key_passes,
                  'into_final_third' : final_third,
                  'into_penalty_area' : ppa,
                  'crosses_into_penalty_area' : crs_ppa,
                  'progressive_passes' : prog
            }
    
        mylist.append(mydict)

    return mylist


def passing_type_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_passing_types'
    
    stats_passing_type = pageSoup.find('table', {'id' : id_})
    stats_passing_type = stats_passing_type.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_passing_type)-1):
        th = stats_passing_type[row].find('th')
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_passing_type[row].find_all('td')
        att = player_[5].text
        live = player_[6].text
        dead = player_[7].text
        fk = player_[8].text
        tb = player_[9].text
        press = player_[10].text
        sw = player_[11].text
        crs = player_[12].text
        ck = player_[13].text
        ck_in = player_[14].text
        ck_out = player_[15].text
        ck_straight = player_[16].text
        height_ground = player_[17].text
        height_low = player_[18].text
        height_high = player_[19].text
        body_left = player_[20].text
        body_right = player_[21].text
        body_head = player_[22].text
        body_ti = player_[23].text
        body_other = player_[24].text
        out_cmp = player_[25].text
        out_off = player_[26].text
        out_out = player_[27].text
        out_int = player_[28].text
        out_blk = player_[29].text
    
        mydict = {'player_id' : id_,
                  'attempted' : att,
                  'live' : live,
                  'dead' : dead,
                  'free_kick' : fk,
                  'through_balls' : tb,
                  'under_pressure' : press,
                  'switches' : sw,
                  'crosses' : crs,
                  'corner_kicks' : ck,
                  'corner_inswing' : ck_in,
                  'corner_outswing' : ck_out,
                  'corner_straight' : ck_straight,
                  'height_ground' : height_ground,
                  'height_low' : height_low,
                  'height_high' : height_high,
                  'body_left' : body_left,
                  'body_right' : body_right,
                  'body_head' : body_head,
                  'body_throw_in' : body_ti,
                  'body_other' : body_other,
                  'completed' : out_cmp,
                  'offsides' : out_off,
                  'out_of_bounds' : out_out,
                  'intercepted' : out_int,
                  'blocked' : out_blk
            }
    
        mylist.append(mydict)

    return mylist


def defensive_actions_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_defense'
    
    stats_defense = pageSoup.find('table', {'id' : id_})
    stats_defense = stats_defense.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_defense)-1):
        th = stats_defense[row].find('th')
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_defense[row].find_all('td')
        tkl = player_[5].text
        tklW = player_[6].text
        tkl_def = player_[7].text
        tkl_mid = player_[8].text
        tkl_att = player_[9].text
        drb_tkl = player_[10].text
        drb_att = player_[11].text
        drb_past = player_[13].text
        press = player_[14].text
        press_succ = player_[15].text
        press_def = player_[17].text
        press_mid = player_[18].text
        press_att = player_[19].text
        blk = player_[20].text
        blk_shots = player_[21].text
        blk_sv = player_[22].text
        blk_pass = player_[23].text
        interceptions = player_[24].text
        clr = player_[26].text
        err = player_[27].text
    
        mydict = {'player_id' : id_,
                  'tackles' : tkl,
                  'tackles_won' : tklW,
                  'tackles_defensive_third' : tkl_def,
                  'tackles_middle_third' : tkl_mid,
                  'tackles_attacking_third' : tkl_att,
                  'dribble_tackles' : drb_tkl,
                  'dribble_tackles_attempted' : drb_att,
                  'dribbled_past' : drb_past,
                  'pressures' : press,
                  'pressures_successful' : press_succ,
                  'pressures_defensive_third' : press_def,
                  'pressures_middle_third' : press_mid,
                  'pressures_attacking_third' : press_att,
                  'blocks' : blk,
                  'blocked_shots' : blk_shots,
                  'blocked_shots_on_target' : blk_sv,
                  'blocked_passes' : blk_pass,
                  'interceptions' : interceptions,
                  'clearances' : clr,
                  'errors' : err
              }
    
        mylist.append(mydict)

    return mylist


def possession_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_possession'
    
    stats_possession = pageSoup.find('table', {'id' : id_})
    stats_possession = stats_possession.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_possession)-1):
        th = stats_possession[row].find('th')
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_possession[row].find_all('td')
        touches = player_[5].text
        touches_def_pen = player_[6].text
        touches_def = player_[7].text
        touches_mid = player_[8].text
        touches_att = player_[9].text
        touches_att_pen = player_[10].text
        touches_live = player_[11].text
        dribble_success = player_[12].text
        dribble_attempted = player_[13].text
        dribble_past = player_[15].text
        dribble_meg = player_[16].text
        carries = player_[17].text
        carries_dist = player_[18].text
        carries_prg_dist = player_[19].text
        passes_targeted = player_[20].text
        passes_received = player_[21].text
        miscon = player_[23].text
        dispos = player_[24].text
    
        mydict = {'player_id' : id_,
                  'touches' : touches,
                  'touches_defensive_pen' : touches_def_pen,
                  'touches_defensive_third' : touches_def,
                  'touches_middle_third' : touches_mid,
                  'touches_attacking_third' : touches_att,
                  'touches_attacking_pen' : touches_att_pen,
                  'touches_live' : touches_live,
                  'dribbles_successful' : dribble_success,
                  'dribbles_attempted' : dribble_attempted,
                  'dribbled_past' : dribble_past,
                  'dribble_megs' : dribble_meg,
                  'carries' : carries,
                  'carry_distance' : carries_dist,
                  'carry_progressive_distance' : carries_prg_dist,
                  'passes_targeted' : passes_targeted,
                  'passes_received' : passes_received,
                  'miscontrols' : miscon,
                  'dispossessed' : dispos
              }
    
        mylist.append(mydict)

    return mylist


def misc_stats(pageSoup, team_id):
    
    id_ = 'stats_' + team_id + '_misc'
    
    stats_miscellaneous = pageSoup.find('table', {'id' : id_})
    stats_miscellaneous = stats_miscellaneous.find_all('tr')
    
    mylist = []
    for row in range(2,len(stats_miscellaneous)-1):
        th = th = stats_miscellaneous[row].find('th')
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        player_ = stats_miscellaneous[row].find_all('td')
        crdY = player_[5].text
        crdR = player_[6].text
        crdY2 = player_[7].text
        fls = player_[8].text
        fld = player_[9].text
        off = player_[10].text
        crs = player_[11].text
        interceptions = player_[12].text
        tklW = player_[13].text
        pk_won = player_[14].text
        pk_con = player_[15].text
        og = player_[16].text
        recov = player_[17].text
        aerial_won = player_[18].text
        aerial_lost = player_[19].text
    
        mydict = {'player_id' : id_,
                  'cards_yellow' : crdY,
                  'cards_red' : crdR,
                  'cards_second_yellow' : crdY2,
                  'fouls' : fls,
                  'fouled' : fld,
                  'offsides' : off,
                  'crosses' : crs,
                  'interceptions' : interceptions,
                  'tackles_won' : tklW,
                  'pk_won' : pk_won,
                  'pk_con' : pk_con,
                  'own_goals' : og,
                  'recoveries' : recov,
                  'aerials_won' : aerial_won,
                  'aerials_lost' : aerial_lost
              }
    
        mylist.append(mydict)

    return mylist


def keeper_stats(pageSoup, team_id):
    
    id_ = 'keeper_stats_' + team_id
    
    stats_keeper = pageSoup.find('table', {'id' : id_})
    stats_keeper = stats_keeper.find('tbody')
    stats_keeper = stats_keeper.find_all('tr')
    
    mylist = []
    for row in range(0,max(1,len(stats_keeper))):
        th = stats_keeper[row].find('th')
        name = th.text
        id_ = th.find('a', href=True)['href'].split('/')[3]
        
        keeper = stats_keeper[row].find_all('td')
        nation = keeper[0].text
        age = keeper[1].text
        minutes = keeper[2].text
        shots_against = keeper[3].text
        goals_allowed = keeper[4].text
        saves = keeper[5].text
        xGA = keeper[7].text
        launched_completed = keeper[8].text
        launched_attempted = keeper[9].text
        passes_attempted = keeper[11].text
        throws_attempted = keeper[12].text
        passes_avg_length = keeper[14].text
        gk_attempted = keeper[15].text
        gk_avg_length = keeper[17].text
        crosses_faced = keeper[18].text
        crosses_stopped = keeper[19].text
        defensive_actions = keeper[21].text
        defensive_actions_avg_distance = keeper[22].text
        
        mydict = {'player_id' : id_,
                  'name' : name,
                  'nation' : nation,
                  'age' : age,
                  'minutes' : minutes,
                  'shots_against' : shots_against,
                  'goals_allowed' : goals_allowed,
                  'saves' : saves,
                  'xGA' : xGA,
                  'launched_completed' : launched_completed,
                  'launched_attempted' : launched_attempted,
                  'passes_attempted' : passes_attempted,
                  'throws_attempted' : throws_attempted,
                  'passes_avg_length' : passes_avg_length,
                  'gk_attempted' : gk_attempted,
                  'gk_avg_length' : gk_avg_length,
                  'crosses_faced' : crosses_faced,
                  'crosses_stopped' : crosses_stopped,
                  'defensive_actions' : defensive_actions,
                  'defensive_actions_avg_distance' : defensive_actions_avg_distance
                  }
    
        mylist.append(mydict)
        
    return mylist


def match_data(url):
    
    page = 'https://fbref.com' + url
    pageTree = requests.get(page, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    
    match_metadata = metadata(pageSoup, url)
    match_lineups = lineups(pageSoup)
    match_stats = team_stats(pageSoup)
    player_stats_x = player_stats(pageSoup, match_metadata['id_x'])
    player_stats_y = player_stats(pageSoup, match_metadata['id_y'])
    passing_stats_x = passing_stats(pageSoup, match_metadata['id_x'])
    passing_stats_y = passing_stats(pageSoup, match_metadata['id_y'])
    passing_type_stats_x = passing_type_stats(pageSoup, match_metadata['id_x'])
    passing_type_stats_y = passing_type_stats(pageSoup, match_metadata['id_y'])
    defensive_stats_x = defensive_actions_stats(pageSoup, match_metadata['id_x'])
    defensive_stats_y = defensive_actions_stats(pageSoup, match_metadata['id_y'])
    possession_stats_x = possession_stats(pageSoup, match_metadata['id_x'])
    possession_stats_y = possession_stats(pageSoup, match_metadata['id_y'])
    misc_stats_x = misc_stats(pageSoup, match_metadata['id_x'])
    misc_stats_y = misc_stats(pageSoup, match_metadata['id_y'])
    keeper_stats_x = keeper_stats(pageSoup, match_metadata['id_x'])
    keeper_stats_y = keeper_stats(pageSoup, match_metadata['id_y'])
    
    
    match = (match_metadata,
             match_lineups,
             match_stats,
             player_stats_x,
             player_stats_y,
             passing_stats_x,
             passing_stats_y,
             passing_type_stats_x,
             passing_type_stats_y,
             defensive_stats_x,
             defensive_stats_y,
             possession_stats_x,
             possession_stats_y,
             misc_stats_x,
             misc_stats_y,
             keeper_stats_x,
             keeper_stats_y)

    return match




matches = []
errors = []
errorsFixed = []

for i in range(0,len(match_urls)):
    
    try:
        match = match_data(match_urls.iloc[i,0])
        matches.append(match)
        
        print(i, 'done')
        time.sleep(random.randint(3,9))
    except:
        errors.append(match_urls.iloc[i,0])
        print(i, 'ERROR')
        time.sleep(random.randint(3,9))
       

with open(outputFolder + 'match_data.pickle', 'wb') as filename:
    pickle.dump(matches, filename)

with open(outputFolder + 'errors_match_data.pickle', 'wb') as filename:
    pickle.dump(errors, filename)

with open(outputFolder + 'match_data_error_fixed.pickle', 'wb') as filename:
    pickle.dump(errorsFixed, filename)

