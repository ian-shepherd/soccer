#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Mon Nov 16 2020
#Last updated Fri Jan 29 2021

#@author: ishepher

#Sources:
    #fbref
#Input: pickle of match stats
#Output: csvs of cleaned data
#
#
#
#
#
#
#~~~~~~INITIAL SETUP~~~~~~

# Packages
import os
import pickle
import pandas as pd
import numpy as np
import datetime as dt
import re

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
inputFolder = rootFolder + '/Data/2. Update/1. Raw/fbref/'
exportFolder = rootFolder + '/Data/2. Update/2. Cleaned/fbref/'

# Load data
with open(inputFolder + 'match_data.pickle', 'rb') as filename:
    pickled_data = pickle.load(filename)
    

# Run if have errors
# with open(inputFolder + 'match_data_error_fixed.pickle', 'rb') as filename:
#     pickled_data_errors = pickle.load(filename)

# pickled_data += pickled_data_errors #[pickled_data_errors] if only 1


#~~~~~EXTRACT DATA~~~~~
 
# Columns
cols_meta = ['id', 'url', 'date', 'kickoff', 'venue', 'attendance',
        'id_x', 'team_x', 'id_y', 'team_y', 'manager_x', 'manager_y', 
        'captain_x', 'captain_id_x', 'captain_y', 'captain_id_y',
        'score_x', 'score_y', 'xg_x', 'xg_y']
cols_officials = ['match_id', 'referee', 'ar1', 'ar2', 'fourth', 'var']
cols_formation = ['match_id', 'formation_x', 'formation_y']
cols_squads = ['match_id', 'team_id', 'id', 'url', 'name']
cols_match_stats = ['match_id', 'possession_x', 'possession_y', 
                   'fouls_x', 'fouls_y', 'corners_x', 'corners_y',
                   'crosses_x', 'crosses_y', 'touches_x', 'touches_y',
                   'tackles_x', 'tackles_y', 'interceptions_x', 'interceptions_y',
                   'aerials_won_x', 'aerials_won_y', 'clearances_x', 'clearances_y',
                   'offsides_x', 'offsides_y', 'goal_kicks_x', 'goal_kicks_y',
                   'throw_ins_x', 'throw_ins_y', 'long_balls_x', 'long_balls_y']
cols_player_stats = ['match_id', 'team_id', 'id', 'name', 'shirtnumber', 
                     'nation', 'position', 'age', 'minutes',
                     'goals', 'assists', 'pk', 'pk_attempted', 'shots', 'shots_on_target',
                     'card_yellow', 'card_red', 'touches', 
                     'pressures', 'tackles', 'interceptions', 'blocks',
                     'xG', 'npxG', 'xA', 'shot_creating_actions', 'goal_creating_actions',
                     'passes_completed', 'passes_attempted', 'pass_progressive_distance',
                     'carries', 'dribble_progressive_distance', 'dribble_success', 'dribble_attempt']
cols_passing_stats = ['match_id', 'team_id', 'id',
                      'completed', 'attempted', 'total_distance', 'progressive_distance',
                      'short_completed', 'short_attempted', 'medium_completed', 'medium_attempted', 'long_completed', 'long_attempted',
                      'assists', 'xA', 'key_passes', 'into_final_third', 'into_pen_area',
                      'crosses_into_pen', 'progressive']
cols_passing_type_stats = ['match_id', 'team_id', 'id',
                           'live', 'dead', 'free_kick', 'through_balls', 'under_pressure',
                           'switches', 'crosses', 'corner_kicks', 'corner_inswing', 'corner_outswing', 'corner_straight',
                           'height_ground', 'height_low', 'height_high', 'body_left', 'body_right', 'body_head', 
                           'body_throw_in', 'body_other', 'completed', 'attempted', 'offsides', 'out_of_bounds', 
                           'intercepted', 'blocked']
cols_defense_stats = ['match_id', 'team_id', 'id', 
                      'tackles', 'tackles_won', 'tackles_defensive_third', 'tackles_middle_third', 'tackles_attacking_third',
                      'dribble_tackles', 'dribble_tackles_attempted', 'dribbled_past',
                      'pressures', 'pressures_successful', 'pressures_defensive_third',
                      'pressures_middle_third', 'pressures_attacking_third', 
                      'blocks', 'blocked_shots', 'blocked_shots_on_target', 'blocked_passes', 'interceptions', 'clearances', 'errors']
cols_possession_stats = ['match_id', 'team_id', 'id', 
                        'touches', 'touches_defensive_pen', 'touches_defensive_third', 'touches_middle_third',
                        'touches_attacking_third', 'touches_attacking_pen', 'touches_live', 
                        'dribbles_successful', 'dribbles_attempted', 'dribbles_past', 'dribble_megs', 
                        'carries', 'carry_distance', 'carry_progressive_distance', 
                        'passes_targeted', 'passes_received', 'miscontrols', 'dispossessed']
cols_misc_stats = ['match_id', 'team_id', 'id',
                  'cards_yellow', 'cards_red', 'cards_second_yellow', 'fouls', 'fouled',
                  'offsides', 'crosses', 'interceptions', 'tackles_won', 'pk_won', 'pk_con', 
                  'own_goals', 'recoveries', 'aerials_lost', 'aerials_won']
cols_keeper_stats = ['match_id', 'team_id', 'id', 'name', 'nation', 'age',
                    'minutes', 'shots_against', 'goals_allowed', 'saves', 'xGA',
                    'launched_completed', 'launched_attempted', 
                    'passes_attempted', 'throws_attempted', 'passes_avg_length',
                    'gk_attempted', 'gk_avg_length', 'crosses_faced', 'crosses_stopped',
                    'defensive_actions', 'defensive_actions_avg_distance']


# Empty dataframs
df_meta_stg = pd.DataFrame(columns = cols_meta)
df_officials_stg = pd.DataFrame(columns = cols_officials)
df_formations_stg = pd.DataFrame(columns = cols_formation)
df_squads_stg = pd.DataFrame(columns = cols_squads)
df_match_stats_stg = pd.DataFrame(columns = cols_match_stats)
df_player_stats_stg = pd.DataFrame(columns = cols_player_stats)
df_player_passing_stats_stg = pd.DataFrame(columns = cols_passing_stats)
df_player_passing_type_stats_stg = pd.DataFrame(columns = cols_passing_type_stats)
df_player_defense_stats_stg = pd.DataFrame(columns = cols_defense_stats)
df_player_possession_stats_stg = pd.DataFrame(columns = cols_possession_stats)
df_player_misc_stats_stg = pd.DataFrame(columns = cols_misc_stats)
df_keeper_stats_stg = pd.DataFrame(columns = cols_keeper_stats)

# Functions
def extract_metadata(mydict):
    
    # metadata
    metadata = mydict
    match_url = metadata.get('url')
    match_id = match_url.split("/")[3]
    date = dt.datetime.strptime(metadata.get('date'), '%Y-%m-%d').date()
    kickoff = metadata.get('kickoff')
    venue = metadata.get('venue')
    attendance = metadata.get('attendance')
    id_x = metadata.get('id_x')
    team_x = metadata.get('team_x')
    id_y = metadata.get('id_y')
    team_y =metadata.get('team_y')
    manager_x = metadata.get('manager_x')
    manager_y = metadata.get('manager_y')
    captain_x = metadata.get('captain_x')
    captain_id_x = captain_x.split("/")[3]
    captain_y = metadata.get('captain_y')
    captain_id_y = captain_y.split("/")[3]
    score_x = metadata.get('score_x')
    score_y = metadata.get('score_y')
    xg_x = metadata.get('xg_x')
    xg_y = metadata.get('xg_y')

    df_meta = pd.DataFrame([[match_id, match_url, date, kickoff, venue, attendance,
                             id_x, team_x, id_y, team_y, manager_x, manager_y,
                             captain_x, captain_id_x, captain_y, captain_id_y,
                             score_x, score_y, xg_x, xg_y]],
                           columns=cols_meta)


    # officials
    officials = metadata.get('officials')
    referee = officials[0].replace(" (Referee)", "")
    ar1 = officials[1].replace(" (AR1)", "")
    ar2 = officials[2].replace(" (AR2)", "")
    fourth = officials[3].replace(" (4th)", "")
    var = (officials[4].replace(" (VAR)", "") if len(officials) > 4 else np.nan)

    df_officials = pd.DataFrame([[match_id, referee, ar1, ar2, fourth, var]],
                                columns = cols_officials)


    return df_meta, df_officials, match_id, id_x, id_y


def extract_formations(mydict, match_id):
    
    pattern = r'\(([^)]+)\)'
    formation_x = re.search(pattern, mydict.get('formation_x')).group(1)
    formation_y = re.search(pattern, mydict.get('formation_y')).group(1)
    
    df = pd.DataFrame([[match_id, formation_x, formation_y]],
                      columns = cols_formation)
    
    return df


def extract_lineups(mydict, match_id, side, team_id):
    
    # home team
    squad_x = mydict.get(side)
    df_x = pd.DataFrame(list(zip(squad_x)), columns = ['url'])
    
    df_x['match_id'] = match_id
    df_x['team_id'] = team_id
    df_x['split_url'] = df_x['url'].str.split("/")
    df_x['id'] = df_x['split_url'].str[3]
    df_x['name'] = df_x['split_url'].str[4]
    df_x = df_x.loc[:,cols_squads]
    
    
    return df_x


def extract_match_stats(mydict, match_id):
    
    aerials_won_x = mydict.get('aerials_won_x')
    aerials_won_y = mydict.get('aerials_won_y')
    clearances_x = mydict.get('clearances_x')
    clearances_y = mydict.get('clearances_y')
    corners_x = mydict.get('corners_x')
    corners_y = mydict.get('corners_y')
    crosses_x = mydict.get('crosses_x')
    crosses_y = mydict.get('crosses_y')
    fouls_x = mydict.get('fouls_x')
    fouls_y = mydict.get('fouls_y')
    goal_kicks_x = mydict.get('goal_kicks_x')
    goal_kicks_y = mydict.get('goal_kicks_y')
    interceptions_x = mydict.get('interceptions_x')
    interceptions_y = mydict.get('interceptions_y')
    long_balls_x = mydict.get('long_balls_x')
    long_balls_y = mydict.get('long_balls_y')
    offsides_x = mydict.get('offsides_x')
    offsides_y = mydict.get('offsides_y')
    possession_x = mydict.get('possession_x')
    possession_y = mydict.get('possession_y')
    tackles_x = mydict.get('tackles_x')
    tackles_y = mydict.get('tackles_y')
    throw_ins_x = mydict.get('throw_ins_x')
    throw_ins_y = mydict.get('throw_ins_y')
    touches_x = mydict.get('touches_x')
    touches_y = mydict.get('touches_y')
    
    df = pd.DataFrame([[match_id, possession_x, possession_y, 
                       fouls_x, fouls_y, corners_x, corners_y,
                       crosses_x, crosses_y, touches_x, touches_y,
                       tackles_x, tackles_y, interceptions_x, interceptions_y,
                       aerials_won_x, aerials_won_y, clearances_x, clearances_y,
                       offsides_x, offsides_y, goal_kicks_x, goal_kicks_y,
                       throw_ins_x, throw_ins_y, long_balls_x, long_balls_y]],
                      columns = cols_match_stats)
    
    return df


def extract_player_stats(mydict, match_id, team_id):
        
    df = pd.DataFrame(columns = cols_player_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        name = mydict_.get('name')
        shirtnumber = mydict_.get('shirtnumber')
        nation = mydict_.get('nation')
        position = mydict_.get('position')
        age = mydict_.get('age')
        minutes = mydict_.get('minutes')
        goals = mydict_.get('goals')
        assists = mydict_.get('assists')
        pk = mydict_.get('pk')
        pk_attempted = mydict_.get('pk_attempted')
        shots = mydict_.get('shots')
        shots_on_target = mydict_.get('shots_on_target')
        card_yellow = mydict_.get('card_yellow')
        card_red = mydict_.get('card_red')
        touches = mydict_.get('touches')
        pressures = mydict_.get('pressures')
        tackles = mydict_.get('tackles')
        interceptions = mydict_.get('interceptions')
        blocks = mydict_.get('blocks')
        xG = mydict_.get('xG')
        npxG = mydict_.get('npxG')
        xA = mydict_.get('xA')
        shot_creating_actions = mydict_.get('shot_creating_actions')
        goal_creating_actions = mydict_.get('goal_creating_actions')
        passes_completed = mydict_.get('passes_completed')
        passes_attempted = mydict_.get('passes_attempted')
        pass_progressive_distance = mydict_.get('pass_progressive_distance')
        carries = mydict_.get('carries')
        dribble_progressive_distance = mydict_.get('dribble_progressive_distance')
        dribble_success = mydict_.get('dribble_success')
        dribble_attempt = mydict_.get('dribble_attempt')
        
        df_ = pd.DataFrame([[match_id, team_id, player_id, name, shirtnumber, 
                            nation, position, age, minutes,
                            goals, assists, pk, pk_attempted, shots, shots_on_target,
                            card_yellow, card_red, touches, 
                            pressures, tackles, interceptions, blocks,
                            xG, npxG, xA, shot_creating_actions, goal_creating_actions,
                            passes_completed, passes_attempted, pass_progressive_distance,
                            carries, dribble_progressive_distance, dribble_success, dribble_attempt]],
                          columns = cols_player_stats)
    
        df = df.append(df_)
    
    return df


def extract_passing_stats(mydict, match_id, team_id):
    
    df = pd.DataFrame(columns = cols_passing_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        completed = mydict_.get('completed')
        attempted = mydict_.get('attempted')
        # attempted = mydict_.get('attemped')
        total_distance = mydict_.get('total_distance')
        progressive_distance = mydict_.get('progressive_distance')
        short_completed = mydict_.get('short_completed')
        short_attempted = mydict_.get('short_attempted')
        medium_completed = mydict_.get('medium_completed')
        medium_attempted = mydict_.get('medium_attempted')
        long_completed = mydict_.get('long_completed')
        long_attempted = mydict_.get('long_attempted')
        assists = mydict_.get('assists')
        xA = mydict_.get('xA')
        key_passes = mydict_.get('key_passes')
        into_final_third = mydict_.get('into_final_third')
        into_penalty_area = mydict_.get('into_penalty_area')
        crosses_into_penalty_area = mydict_.get('crosses_into_penalty_area')
        progressive_passes = mydict_.get('progressive_passes')

        df_ = pd.DataFrame([[match_id, team_id, player_id, completed, attempted, 
                             total_distance, progressive_distance, short_completed, short_attempted,
                             medium_completed, medium_attempted, long_completed, long_attempted,
                             assists, xA, key_passes, into_final_third, into_penalty_area,
                             crosses_into_penalty_area, progressive_passes]],
                             columns = cols_passing_stats)
                             
                             
        df = df.append(df_)

    
    return df


def extract_passing_type_stats(mydict, match_id, team_id):
    
    df = pd.DataFrame(columns = cols_passing_type_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        live = mydict_.get('live')
        dead = mydict_.get('dead')
        free_kick = mydict_.get('free_kick')
        through_balls = mydict_.get('through_balls')
        under_pressure = mydict_.get('under_pressure')
        switches = mydict_.get('switches')
        crosses = mydict_.get('crosses')
        corner_kicks = mydict_.get('corner_kicks')
        corner_inswing = mydict_.get('corner_inswing')
        corner_outswing = mydict_.get('corner_outswing')
        corner_straight = mydict_.get('corner_straight')
        height_ground = mydict_.get('height_ground')
        height_low = mydict_.get('height_low')
        height_high = mydict_.get('height_high')
        body_left = mydict_.get('body_left')
        body_right = mydict_.get('body_right')
        body_head = mydict_.get('body_head')
        body_throw_in = mydict_.get('body_throw_in')
        body_other = mydict_.get('body_other')
        completed = mydict_.get('completed')
        attempted = mydict_.get('attempted')
        offsides = mydict_.get('offsides')
        out_of_bounds = mydict_.get('out_of_bounds')
        intercepted = mydict_.get('intercepted')
        blocked = mydict_.get('blocked')

        df_ = pd.DataFrame([[match_id, team_id, player_id,
                             live, dead, free_kick, through_balls, under_pressure, switches, crosses, 
                             corner_kicks, corner_inswing, corner_outswing, corner_straight, 
                             height_ground, height_low, height_high, 
                             body_left, body_right, body_head, body_throw_in, body_other, 
                             completed, attempted, offsides, out_of_bounds, intercepted, blocked]],
                             columns = cols_passing_type_stats)
        
        df = df.append(df_)
    
    return df


def extract_defense_stats(mydict, match_id, team_id):
    
    df = pd.DataFrame(columns = cols_defense_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        tackles = mydict_.get('tackles')
        tackles_won = mydict_.get('tackles_won')
        tackles_defensive_third = mydict_.get('tackles_defensive_third')
        tackles_middle_third = mydict_.get('tackles_middle_third')
        tackles_attacking_third = mydict_.get('tackles_attacking_third')
        dribble_tackles = mydict_.get('dribble_tackles')
        dribble_tackles_attempted = mydict_.get('dribble_tackles_attempted')
        dribbled_past = mydict_.get('dribbled_past')
        pressures = mydict_.get('pressures')
        pressures_successful = mydict_.get('pressures_successful')
        pressures_defensive_third = mydict_.get('pressures_defensive_third')
        pressures_middle_third = mydict_.get('pressures_middle_third')
        pressures_attacking_third = mydict_.get('pressures_attacking_third')
        blocks = mydict_.get('blocks')
        blocked_shots = mydict_.get('blocked_shots')
        blocked_shots_on_target = mydict_.get('blocked_shots_on_target')
        blocked_passes = mydict_.get('blocked_passes')
        interceptions = mydict_.get('interceptions')
        clearances = mydict_.get('clearances')
        errors = mydict_.get('errors')

        df_ = pd.DataFrame([[match_id, team_id, player_id, 
                             tackles, tackles_won, tackles_defensive_third, tackles_middle_third, tackles_attacking_third, 
                             dribble_tackles, dribble_tackles_attempted, dribbled_past, 
                             pressures, pressures_successful, pressures_defensive_third, 
                             pressures_middle_third, pressures_attacking_third,
                             blocks, blocked_shots, blocked_shots_on_target, blocked_passes, interceptions, clearances, errors]],
                             columns = cols_defense_stats)
        
        df = df.append(df_)
    
    
    return df


def extract_possession_stats(mydict, match_id, team_id):
    
    df = pd.DataFrame(columns = cols_possession_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        touches = mydict_.get('touches')
        touches_defensive_pen = mydict_.get('touches_defensive_pen')
        touches_defensive_third = mydict_.get('touches_defensive_third')
        touches_middle_third = mydict_.get('touches_middle_third')
        touches_attacking_third = mydict_.get('touches_attacking_third')
        touches_attacking_pen = mydict_.get('touches_attacking_pen')
        touches_live = mydict_.get('touches_live')
        dribbles_successful = mydict_.get('dribbles_successful')
        dribbles_attempted = mydict_.get('dribbles_attempted')
        dribbled_past = mydict_.get('dribbled_past')
        dribble_megs = mydict_.get('dribble_megs')
        # dribble_megs = mydict_.get('pribble_megs')
        carries = mydict_.get('carries')
        carry_distance = mydict_.get('carry_distance')
        carry_progressive_distance = mydict_.get('carry_progressive_distance')
        passes_targeted = mydict_.get('passes_targeted')
        passes_received = mydict_.get('passes_received')
        miscontrols = mydict_.get('miscontrols')
        dispossessed = mydict_.get('dispossessed')

        
        df_ = pd.DataFrame([[match_id, team_id, player_id, 
                            touches, touches_defensive_pen, touches_defensive_third, touches_middle_third,
                            touches_attacking_third, touches_attacking_pen, touches_live,
                            dribbles_successful, dribbles_attempted, dribbled_past, dribble_megs,
                            carries, carry_distance, carry_progressive_distance, 
                            passes_targeted, passes_received, miscontrols, dispossessed]],
                            columns = cols_possession_stats)
        
        df = df.append(df_)


    return df


def extract_misc_stats(mydict, match_id, team_id):
    
    df = pd.DataFrame(columns = cols_misc_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        cards_yellow = mydict_.get('cards_yellow')
        cards_red = mydict_.get('cards_red')
        cards_second_yellow = mydict_.get('cards_second_yellow')
        fouls = mydict_.get('fouls')
        fouled = mydict_.get('fouled')
        offsides = mydict_.get('offsides')
        crosses = mydict_.get('crosses')
        interceptions = mydict_.get('interceptions')
        tackles_won = mydict_.get('tackles_won')
        pk_won = mydict_.get('pk_won')
        pk_con = mydict_.get('pk_con')
        own_goals = mydict_.get('own_goals')
        recoveries = mydict_.get('recoveries')
        aerials_lost = mydict_.get('aerials_lost')
        aerials_won = mydict_.get('aerials_won')

        
        df_ = pd.DataFrame([[match_id, team_id, player_id, 
                             cards_yellow, cards_red, cards_second_yellow, fouls, fouled,
                             offsides, crosses, interceptions, tackles_won, pk_won, pk_con,
                             own_goals, recoveries, aerials_lost, aerials_won]],
                             columns = cols_misc_stats)
        
        df = df.append(df_)

    
    return df


def extract_keepr_stats(mydict, match_id, team_id):

    
    df = pd.DataFrame(columns = cols_keeper_stats)
    
    for i in range(0,len(mydict)):
        
        mydict_ = mydict[i]
        player_id = mydict_.get('player_id')
        name = mydict_.get('name')
        nation = mydict_.get('nation')
        age = mydict_.get('age')
        minutes = mydict_.get('minutes')
        shots_against = mydict_.get('shots_against')
        goals_allowed = mydict_.get('goals_allowed')
        saves = mydict_.get('saves')
        xGA = mydict_.get('xGA')
        launched_completed = mydict_.get('launched_completed')
        launched_attempted = mydict_.get('launched_attempted')
        passes_attempted = mydict_.get('passes_attempted')
        throws_attempted = mydict_.get('throws_attempted')
        passes_avg_length = mydict_.get('passes_avg_length')
        gk_attempted = mydict_.get('gk_attempted')
        gk_avg_length = mydict_.get('gk_avg_length')
        crosses_faced = mydict_.get('crosses_faced')
        crosses_stopped = mydict_.get('crosses_stopped')
        defensive_actions = mydict_.get('defensive_actions')
        defensive_actions_avg_distance = mydict_.get('defensive_actions_avg_distance')
        
        df_ = pd.DataFrame([[match_id, team_id, player_id, name, nation, age, minutes,
                            shots_against, goals_allowed, saves, xGA,
                            launched_completed, launched_attempted, 
                            passes_attempted, throws_attempted, passes_avg_length,
                            gk_attempted, gk_avg_length, crosses_faced, crosses_stopped,
                            defensive_actions, defensive_actions_avg_distance]],
                          columns = cols_keeper_stats)
        
        
    
        df = df.append(df_)
    
    return df



def match(mytuple):
    
    metadata, officials, match_id, id_x, id_y = extract_metadata(mytuple[0])
    formation = extract_formations(mytuple[1], match_id)
    squad_x = extract_lineups(mytuple[1], match_id, 'squad_x', id_x)
    squad_y = extract_lineups(mytuple[1], match_id, 'squad_y', id_y)
    match_stats = extract_match_stats(mytuple[2], match_id)
    player_stats_x = extract_player_stats(mytuple[3], match_id, id_x)
    player_stats_y = extract_player_stats(mytuple[4], match_id, id_y)
    
    player_passing_stats_x = extract_passing_stats(mytuple[5], match_id, id_x)
    player_passing_stats_y = extract_passing_stats(mytuple[6], match_id, id_y)
    player_passing_types_stats_x = extract_passing_type_stats(mytuple[7], match_id, id_x)
    player_passing_types_stats_y = extract_passing_type_stats(mytuple[8], match_id, id_y)
    player_defensive_stats_x = extract_defense_stats(mytuple[9], match_id, id_x)
    player_defensive_stats_y = extract_defense_stats(mytuple[10], match_id, id_y)
    player_possession_stats_x = extract_possession_stats(mytuple[11], match_id, id_x)
    player_possession_stats_y = extract_possession_stats(mytuple[12], match_id, id_y)
    player_misc_stats_x = extract_misc_stats(mytuple[13], match_id, id_x)
    player_misc_stats_y = extract_misc_stats(mytuple[14], match_id, id_y)
    
    
    
    keeper_stats_x = extract_keepr_stats(mytuple[15], match_id, id_x)
    keeper_stats_y = extract_keepr_stats(mytuple[16], match_id, id_y)
    
    return metadata, officials, formation, squad_x, squad_y, \
            match_stats, player_stats_x, player_stats_y, player_passing_stats_x, player_passing_stats_y, \
            player_passing_types_stats_x, player_passing_types_stats_y, player_defensive_stats_x, player_defensive_stats_y, \
            player_possession_stats_x, player_possession_stats_y, player_misc_stats_x, player_misc_stats_y, \
            keeper_stats_x, keeper_stats_y


# Create dataframes from all match dictionaries
for i in range(0,len(pickled_data)):
    
    data = match(pickled_data[i])
    
    df_meta_stg = df_meta_stg.append(data[0])
    df_officials_stg = df_officials_stg.append(data[1])
    df_formations_stg = df_formations_stg.append(data[2])
    df_squads_stg = df_squads_stg.append(data[3])
    df_squads_stg = df_squads_stg.append(data[4])
    df_match_stats_stg = df_match_stats_stg.append(data[5])
    df_player_stats_stg = df_player_stats_stg.append(data[6])
    df_player_stats_stg = df_player_stats_stg.append(data[7])
    df_player_passing_stats_stg = df_player_passing_stats_stg.append(data[8])
    df_player_passing_stats_stg = df_player_passing_stats_stg.append(data[9])
    df_player_passing_type_stats_stg = df_player_passing_type_stats_stg.append(data[10])
    df_player_passing_type_stats_stg = df_player_passing_type_stats_stg.append(data[11])
    df_player_defense_stats_stg = df_player_defense_stats_stg.append(data[12])
    df_player_defense_stats_stg = df_player_defense_stats_stg.append(data[13])
    df_player_possession_stats_stg = df_player_possession_stats_stg.append(data[14])
    df_player_possession_stats_stg = df_player_possession_stats_stg.append(data[15])
    df_player_misc_stats_stg = df_player_misc_stats_stg.append(data[16])
    df_player_misc_stats_stg = df_player_misc_stats_stg.append(data[17])
    df_keeper_stats_stg = df_keeper_stats_stg.append(data[18])
    df_keeper_stats_stg = df_keeper_stats_stg.append(data[19])
    
    print(str(i) + ' done')
    
del data, cols_meta, cols_officials, cols_formation, cols_squads, cols_match_stats, \
    cols_player_stats, cols_passing_stats, cols_passing_type_stats, cols_defense_stats, \
    cols_possession_stats, cols_misc_stats, cols_keeper_stats



#~~~~~CLEAN DATA~~~~~

def clean_meta_stg(df):
    
    df['attendance'] = np.where(df['attendance'].isnull(), "0", df['attendance'])
    df['attendance'] = df['attendance'].str.replace("Attendance: ", "")
    df['attendance'] = df['attendance'].str.replace(",", "")
    
    convert_dict = {'attendance' : int,
                    'score_x' : int,
                    'score_y' : int,
                    'xg_x' : float,
                    'xg_y' : float}
    df = df.astype(convert_dict)
    
    df = df.reset_index(drop=True)
    
    return df


def clean_match_stats_stg(df):
    
    df['possession_x'] = df['possession_x'].str.replace('%', '').astype(int) / 100
    df['possession_y'] = df['possession_y'].str.replace('%', '').astype(int) / 100
    float_cols = ['fouls_x', 'fouls_y', 'corners_x', 'corners_y', 'crosses_x', 'crosses_y',
                'touches_x', 'touches_y', 'tackles_x', 'tackles_y', 
                'interceptions_x', 'interceptions_y', 'aerials_won_x', 'aerials_won_y',
                'clearances_x', 'clearances_y', 'offsides_x', 'offsides_y', 
                'goal_kicks_x', 'goal_kicks_y', 'throw_ins_x', 'throw_ins_y',
                'long_balls_x', 'long_balls_y']
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    df = df.reset_index(drop=True)
    
    return df


def clean_player_stats_stg(df):
    
    df['age'] = df['age'].replace("", "0-0")
    df['age'] = df['age'].str.split('-')
    df['age'] = df['age'].str[0].astype(int) + df['age'].str[1].astype(int)/365
    
    
    float_cols = ['minutes', 'goals', 'assists', 'pk', 'pk_attempted', 
                  'shots', 'shots_on_target', 'card_yellow', 'card_red', 'touches',
                  'pressures', 'tackles', 'interceptions', 'blocks', 'xG', 'npxG', 'xA',
                  'shot_creating_actions', 'goal_creating_actions', 'passes_completed',
                  'passes_attempted', 'pass_progressive_distance', 'carries',
                  'dribble_progressive_distance', 'dribble_success', 'dribble_attempt']
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    df = df.reset_index(drop=True)
    
    return df


def clean_passing_stats_stg(df):
    
    
    float_cols = ['completed', 'attempted', 'total_distance',
                  'progressive_distance', 'short_completed', 'short_attempted',
                  'medium_completed', 'medium_attempted', 'long_completed',
                  'long_attempted', 'assists', 'xA', 'key_passes', 'into_final_third',
                  'into_pen_area', 'crosses_into_pen', 'progressive']
    
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    
    df = df.reset_index(drop=True)
    
    return df


def clean_passing_type_stats_stg(df):
    
    float_cols = ['live', 'dead', 'free_kick',
                  'through_balls', 'under_pressure', 'switches', 'crosses',
                  'corner_kicks', 'corner_inswing', 'corner_outswing', 'corner_straight',
                  'height_ground', 'height_low', 'height_high', 'body_left', 'body_right',
                  'body_head', 'body_throw_in', 'body_other', 'completed', 'attempted',
                  'offsides', 'out_of_bounds', 'intercepted', 'blocked']
    
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    
    df = df.reset_index(drop=True)
    
    return df


def clean_defensive_stats_stg(df):
    
    
    float_cols = ['tackles', 'tackles_won',
                  'tackles_defensive_third', 'tackles_middle_third',
                  'tackles_attacking_third', 'dribble_tackles',
                  'dribble_tackles_attempted', 'dribbled_past', 'pressures',
                  'pressures_successful', 'pressures_defensive_third',
                  'pressures_middle_third', 'pressures_attacking_third', 'blocks',
                  'blocked_shots', 'blocked_shots_on_target', 'blocked_passes',
                  'interceptions', 'clearances', 'errors']
    
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    
    df = df.reset_index(drop=True)
    
    return df


def clean_possession_stats_stg(df):
    
    
    float_cols = ['touches', 'touches_defensive_pen',
                  'touches_defensive_third', 'touches_middle_third',
                  'touches_attacking_third', 'touches_attacking_pen', 'touches_live',
                  'dribbles_successful', 'dribbles_attempted', 'dribbles_past',
                  'dribble_megs', 'carries', 'carry_distance',
                  'carry_progressive_distance', 'passes_targeted', 'passes_received',
                  'miscontrols', 'dispossessed']
    
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    
    df = df.reset_index(drop=True)
    
    return df


def clean_misc_stats_stg(df):
    
    
    float_cols = ['cards_yellow', 'cards_red',
                  'cards_second_yellow', 'fouls', 'fouled', 'offsides', 'crosses',
                  'interceptions', 'tackles_won', 'pk_won', 'pk_con', 'own_goals',
                  'recoveries', 'aerials_lost', 'aerials_won']
    
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    
    df = df.reset_index(drop=True)
    
    return df


def clean_keeper_stats_stg(df):
    
    df = df_keeper_stats_stg.copy()
    df['age'] = df['age'].replace("", "0-0")
    df['age'] = df['age'].str.split('-')
    df['age'] = df['age'].str[0].astype(int) + df['age'].str[1].astype(int)/365
    
    
    float_cols = ['minutes', 'shots_against', 'goals_allowed', 'saves',  'xGA',
                  'launched_completed', 'launched_attempted', 'passes_attempted', 'throws_attempted',
                  'passes_avg_length', 'gk_attempted', 'gk_avg_length', 'crosses_faced', 
                  'crosses_stopped', 'defensive_actions', 'defensive_actions_avg_distance']
    df[float_cols] = df[float_cols].replace("", "0")
    df[float_cols] = df[float_cols].astype(float)
    
    df = df.reset_index(drop=True)
    
    return df


df_meta_stg = clean_meta_stg(df_meta_stg)
df_officials_stg = df_officials_stg.reset_index(drop=True) #no cleaning needed
df_formations_stg['formation_x'] = df_formations_stg['formation_x'].str.replace('◆', '(d)')
df_formations_stg['formation_y'] = df_formations_stg['formation_y'].str.replace('◆', '(d)')
df_formations_stg = df_formations_stg.reset_index(drop=True) #no other cleaning needed
df_squads_stg = df_squads_stg.reset_index(drop=True) #no cleaning needed
df_match_stats_stg = clean_match_stats_stg(df_match_stats_stg)
df_player_stats_stg = clean_player_stats_stg(df_player_stats_stg)
df_player_passing_stats_stg = clean_passing_stats_stg(df_player_passing_stats_stg)
df_player_passing_type_stats_stg = clean_passing_type_stats_stg(df_player_passing_type_stats_stg)
df_player_defense_stats_stg = clean_defensive_stats_stg(df_player_defense_stats_stg)
df_player_possession_stats_stg = clean_possession_stats_stg(df_player_possession_stats_stg)
df_player_misc_stats_stg = clean_misc_stats_stg(df_player_misc_stats_stg)
df_keeper_stats_stg = clean_keeper_stats_stg(df_keeper_stats_stg)




#~~~~~EXPORT DATA~~~~~
df_meta_stg.to_csv(exportFolder + 'metadata.csv', index=False)
df_officials_stg.to_csv(exportFolder + 'officials.csv', index=False)
df_formations_stg.to_csv(exportFolder + 'formations.csv', index=False)
df_squads_stg.to_csv(exportFolder + 'squads.csv', index=False)
df_match_stats_stg.to_csv(exportFolder + 'match_stats.csv', index=False)
df_player_stats_stg.to_csv(exportFolder + 'player_stats.csv', index=False)
df_player_passing_stats_stg.to_csv(exportFolder + 'player_passing_stats.csv', index=False)
df_player_passing_type_stats_stg.to_csv(exportFolder + 'player_passing_type_stats.csv', index=False)
df_player_defense_stats_stg.to_csv(exportFolder + 'player_defense_stats.csv', index=False)
df_player_possession_stats_stg.to_csv(exportFolder + 'player_possession_stats.csv', index=False)
df_player_misc_stats_stg.to_csv(exportFolder + 'player_misc_stats.csv', index=False)
df_keeper_stats_stg.to_csv(exportFolder + 'keeper_stats.csv', index=False)
