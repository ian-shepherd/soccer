#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Jan 30 2021
#Last updated Sun Mar 14 2021

#@author: ishepher

#Input: csvs
#Output: web app 
#
#
#
#
#
#
#~~~~~~INITIAL SETUP~~~~~~

# Packages
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import seaborn as sns
from math import pi



plt.style.use('seaborn')
sns.set_style(style='white')

# Folder paths
dataFolder = 'https://github.com/ian-shepherd/soccer/blob/main/Data/'

# Use the full page instead of a narrow central column
st.set_page_config(page_title='Soccer Dashboard',
                   page_icon='https://raw.githubusercontent.com/papagorgio23/Python101/master/newlogo.png',
                   layout="wide")


@st.cache



#~~~~~FUNCTIONS~~~~~

# Import data
def load_data():
    
    # player dim
    player_dim = pd.read_csv(dataFolder + 'player_dim.csv', usecols=['fbref', 'transfermarkt', 'name', 'position_main', 'born', 'birth_place',
                                                                     'nationality', 'height', 'foot', 'club', 'contracted', 'mv'])
    player_dim['born'] = pd.to_datetime(player_dim['born']).dt.date
    player_dim['contracted'] = pd.to_datetime(player_dim['contracted']).dt.date
    player_dim = player_dim[player_dim['club'].notnull()]
    player_dim = player_dim[player_dim['position_main']!='Goalkeeper']
    pos_dict = {
        'Centre-Back' : 'CB',
        'Centre-Forward': 'ST',
        'Central Midfield' : 'CM/DM',
        'Right-Back' : 'FB',
        'Defensive Midfield' : 'CM/DM',
        'Left-Back' : 'FB',
        'Left Winger' : 'Winger/AM',
        'Right Winger' : 'Winger/AM',
        'Attacking Midfield' : 'Winger/AM',
        'Left Midfield' : 'WM',
        'Right Midfield' : 'WM',
        'Second Striker' : 'ST'}
    player_dim['pos_group'] = player_dim['position_main'].map(pos_dict)
    
    player_dim['player_slicer'] = player_dim['name'] + ' (' + player_dim['club'] + '-' + player_dim['fbref'] +')'
    
    # team_dim
    team_dim = pd.read_csv(dataFolder + 'team_dim.csv', usecols=['fbref', 'transfermarkt_name', 'primary_color', 'secondary_color', 'alternate_color'])
    
    # match_dim
    match_dim = pd.read_csv(dataFolder + 'match_dim.csv')
    match_dim['date'] = pd.to_datetime(match_dim['date']).dt.date
    
    # match_stats_fact
    matchday_stats_fact = pd.read_csv(dataFolder + 'matchday_stats_fact.csv', usecols=['match_id', 'possession_x', 'possession_y'])
    matchday_stats_fact = matchday_stats_fact.merge(match_dim.loc[:,['id', 'id_x', 'id_y']], how='inner', left_on='match_id', right_on='id').drop(columns=['id'])
    matchday_stats_fact_x = matchday_stats_fact.loc[:,['match_id', 'id_x', 'possession_x']]
    matchday_stats_fact_x.columns = ['match_id', 'team_id', 'possession']
    matchday_stats_fact_y = matchday_stats_fact.loc[:,['match_id', 'id_y', 'possession_y']]
    matchday_stats_fact_y.columns = ['match_id', 'team_id', 'possession']
    matchday_stats_fact = pd.concat([matchday_stats_fact_x, matchday_stats_fact_y], ignore_index=True)
    
    # v_player_match_stats_fact
    v_player_match_stats_fact = pd.read_csv(dataFolder + 'v_player_match_stats_fact.csv',
                                            usecols=['match_id', 'team_id', 'player_id', 'position',
                                                   'minutes', 'goals', 'assists', 'pk', 'xG', 'shots', 'shots_on_target', 'shot_creating_actions',
                                                   'passes_attempted', 'passes_completed', 'dribble_progressive_distance', 'dribble_success',
                                                   'pressures', 'tackles', 'interceptions', 'blocks', 'clearances', 'dribbled_past',
                                                   'key_passes', 'into_final_third', 'pass_progressive_distance',
                                                   'crosses', 'through_balls',
                                                   'touches', 'dispossessed', 'touches_attacking_pen',
                                                   'fouled', 'fouls', 'aerials_won', 'aerials_lost', 'recoveries'])
    
    # custom stats
    v_player_match_stats_fact['npG'] = v_player_match_stats_fact['goals'] - v_player_match_stats_fact['pk']
    v_player_match_stats_fact['goal_contributions'] = v_player_match_stats_fact['goals'] + v_player_match_stats_fact['assists']  
    v_player_match_stats_fact['tkl+int'] = v_player_match_stats_fact['tackles'] + v_player_match_stats_fact['interceptions']
    
    # possession adjust
    v_player_match_stats_fact = v_player_match_stats_fact.merge(matchday_stats_fact, how='inner', on=['match_id', 'team_id'])
    v_player_match_stats_fact['pAdj'] = (.5 / (1 - v_player_match_stats_fact['possession']))
    v_player_match_stats_fact['pAdjTkl'] =  v_player_match_stats_fact['pAdj'] * v_player_match_stats_fact['tackles']
    v_player_match_stats_fact['pAdjInt'] =  v_player_match_stats_fact['pAdj'] * v_player_match_stats_fact['interceptions']
    v_player_match_stats_fact['pAdjClearances'] =  v_player_match_stats_fact['pAdj'] * v_player_match_stats_fact['clearances']
    v_player_match_stats_fact['pAdjDribbled_Past'] =  v_player_match_stats_fact['pAdj'] * v_player_match_stats_fact['dribbled_past']
    v_player_match_stats_fact = v_player_match_stats_fact.drop(columns=['pAdj'])

    # trans_mv_fact
    trans_mv_fact = pd.read_csv(dataFolder + 'trans_mv_fact.csv')
    trans_mv_fact['date'] = pd.to_datetime(trans_mv_fact['date']).dt.date
    
    # lists
    player_list = player_dim['player_slicer'].tolist()
    season_list = match_dim['season'].unique().tolist()
    
    
    return player_dim, team_dim, match_dim, v_player_match_stats_fact, trans_mv_fact, player_list, season_list


def filter_data(match_dim, v_player_match_stats_fact, selected_seasons=['20/21']):
    
    selected_seasons = [selected_seasons] if isinstance(selected_seasons, str) else selected_seasons
    match_dim = match_dim[match_dim['season'].isin(selected_seasons)]
    v_player_match_stats_fact = v_player_match_stats_fact.merge(match_dim.loc[:,['id']], how='inner', left_on='match_id', right_on='id').drop(columns=['id'])
    
    return match_dim, v_player_match_stats_fact



# Row 2
def demographic(df, player_id):
    
    df = df[df['fbref']==player_id]
    
    born = df.loc[:,'born'].iloc[0]
    birth_place = df.loc[:,'birth_place'].iloc[0]
    nationality = df.loc[:,'nationality'].iloc[0]
    height = df.loc[:,'height'].iloc[0]
    foot = df.loc[:,'foot'].iloc[0]
    
    position = df.loc[:,'position_main'].iloc[0]
    market_value = df.loc[:,'mv'].iloc[0]
    contract_until = df.loc[:,'contracted'].iloc[0]
    age = relativedelta(dt.date.today(), born).years
    mv = (str(market_value.astype(float)/1000000) + 'm' if market_value>=1000000 else str(int(market_value.astype(float)/1000)) + "k")
    club = df.loc[:,'club'].iloc[0]
    name = df.loc[:,'name'].iloc[0]
    
    
    return name, position, born, age, birth_place, nationality, height, foot, club, contract_until, mv


def kpis(df, player_id):
    
    df = df[df['player_id']==player_id]
    df = df[df['player_id']==player_id]
    
    cols = ['player_id', 'minutes', 'goals', 'assists', 'xG', 'shot_creating_actions']
    df = df.loc[:,cols]
    df = df.groupby(['player_id']).sum()
    
    
    mins = df['minutes'].iloc[0]
    gls = df['goals'].iloc[0]
    ast = df['assists'].iloc[0]
    xg = df['xG'].iloc[0]
    sca = df['shot_creating_actions'].iloc[0]
    
    
    return mins, gls, ast, xg, sca, df


def percentiles(df, player_dim, player_id, pos_group, min_filter):
    
    
    # Create copies of data
    playerStatsDF = df.copy()
    
    # Filter position group
    player_dim = player_dim[player_dim['pos_group']==pos_group]
    playerStatsDF = playerStatsDF.merge(player_dim.loc[:,['fbref']], how='inner', left_on='player_id', right_on='fbref').drop(columns=['fbref'])
    
    # Filter minimum minutes
    players = playerStatsDF.loc[:,['player_id', 'minutes']]
    players = players.groupby(['player_id']).sum()
    players = players[players['minutes']>=min_filter]
    players = players.drop(columns=['minutes'])       
    
    # Aggregate per 90
    df = players.merge(playerStatsDF, how='inner', on=['player_id'])
    df = df.groupby(['player_id']).sum()
    mask = ~(df.columns.isin(['minutes', 'xG/shot', 'shooting%', 'passing%']))
    agg_cols = df.columns[mask].tolist()
    df.loc[:, agg_cols] = df.loc[:, agg_cols].div(df['minutes'], axis=0) * 90  
    df = df.drop(columns=['minutes'])
    
    # Add rates
    df['xG/shot'] = df['xG'] / df['shots']
    df['shooting%'] = df['shots_on_target'] / df['shots']
    df['passing%'] = df['passes_completed'] / df['passes_attempted']
    df['aerial%'] = df['aerials_won'] / (df['aerials_won'] + df['aerials_lost'])
    
    # Split data
    p90 = df.loc[player_id,:]
    percentiles = df.copy()
    
    # Get percentiles
    for col in percentiles.columns:
        percentiles.loc[:,col] = percentiles[col].rank(pct=True)
    
    # Reverse percentiles where high = bad
    percentiles['dispossessed'] = 1 - percentiles['dispossessed']
    percentiles['fouls'] = 1 - percentiles['fouls']
    percentiles['dribbled_past'] = 1 - percentiles['dribbled_past']
    percentiles['pAdjDribbled_Past'] = 1 - percentiles['pAdjDribbled_Past']
    
    # Filter for player
    percentiles = percentiles.reset_index()
    percentiles = percentiles[percentiles['player_id']==player_id]       
             
    
    return percentiles, p90


def radar(df, pos_group, club_color, df2="", club_color2=""):
    
    
    # Cols measured
    attack_cols = ['npG', 'shots', 'shooting%', 'passing%', 'key_passes', 'through_balls',
                   'tkl+int', 'dispossessed', 'dribble_success', 'xG/shot']
    wm_cols = ['passing%', 'key_passes', 'through_balls', 'crosses', 'goal_contributions', 
               'tkl+int', 'dispossessed', 'dribble_success', 'recoveries', 'aerials_won']
    cm_cols = ['passing%', 'key_passes', 'through_balls', 'goal_contributions', 'dribble_success',
               'dispossessed', 'fouls', 'dribbled_past', 'pAdjTkl', 'pAdjInt', 'pass_progressive_distance']
    fb_cols = ['pAdjTkl', 'pAdjInt', 'passing%', 'key_passes', 'crosses', 'into_final_third',
               'dribble_success', 'aerials_won', 'dribbled_past', 'fouls', 'recoveries']
    cb_cols = ['passing%', 'pAdjDribbled_Past', 'pAdjTkl', 'pAdjInt', 'blocks',
               'pAdjClearances', 'fouls', 'aerials_won', 'pass_progressive_distance']
    
    pos_cols = {
        'ST' : attack_cols,
        'Winger/AM' : attack_cols,
        'WM' : wm_cols,
        'CM/DM' : cm_cols,
        'FB' : fb_cols,
        'CB' : cb_cols
        }
    cols = pos_cols.get(pos_group)
    
    df = df.loc[:, cols]
    
    # Rename stats
    df = df.rename(columns={'dribble_success' : 'successful\ndribbles',
                            'through_balls' : 'through balls',
                            'key_passes' : 'key passes',
                            'pass_progressive_distance' : 'pass progressive\ndistance',
                            'goal_contributions' : 'G+A',
                            'pAdjDribbled_Past' : 'pAdjDribbled\npast',
                            'dribbled_past' : 'dribbled past',
                            'aerials_won' : 'aerials won',
                            'into_final_third' : 'passes into\nfinal third'})
    
    # Create  background
    # number of variables
    stats = df.columns
    N = len(stats)
    
    # axis angles
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Plot figure
    fig = plt.figure() #5,5
    
    # initialize spider plot
    ax = plt.subplot(111, polar=True)
    
    # set first axis on top
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    # draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], stats, fontsize=8)

    # for label,i in zip(ax.get_xticklabels(),range(0,len(angles))):!
    for label, theta in zip(ax.get_xticklabels(), angles):

        # angle_rad=angles[i]
        angle_rad = theta

        if angle_rad == 0:
            ha='center'
            va='bottom'
        elif angle_rad == pi:
            ha='center'
            va='top'
        elif angle_rad <= pi/2:
            ha= 'left'
            va= "bottom"
        elif pi/2 < angle_rad <= pi:
            ha= 'left'
            va= "top"
        elif pi < angle_rad <= (3*pi/2):
            ha= 'right'
            va= "top"  
        else:
            ha= 'right'
            va= "bottom"
            
        label.set_verticalalignment(va)
        label.set_horizontalalignment(ha)

    # draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([.2,.4, .6, .8, 1], ["0.2","0.4","0.6", "0.8", ""], color="grey", size=7)
    plt.ylim(0,1)
    
    # Add data
    values = df.values.flatten().tolist()
    values += values[:1]
    
    ax.plot(angles, values, color=club_color, linewidth=1, linestyle='solid', label='Player1')
    ax.fill(angles, values, color=club_color, alpha=0.25)
    
    
    if isinstance(df2, pd.DataFrame):
        
        df2 = df2.loc[:, cols]
        # Rename stats
        df2 = df2.rename(columns={'dribble_success' : 'successful\ndribbles',
                                  'through_balls' : 'through balls',
                                  'key_passes' : 'key passes',
                                  'pass_progressive_distance' : 'pass progressive\ndistance',
                                  'goal_contributions' : 'G+A',
                                  'pAdjDribbled_Past' : 'pAdjDribbled\npast',
                                  'dribbled_past' : 'dribbled past',
                                  'aerials_won' : 'aerials won',
                                  'into_final_third' : 'passes into\nfinal third'})
        
        
        # Add player2 data
        values2 = df2.values.flatten().tolist()
        values2 += values2[:1]
        
        ax.plot(angles, values2, color=club_color2, linewidth=1, linestyle='solid', label='Player2')
        ax.fill(angles, values2, color=club_color2, alpha=0.25)
        
        plt.legend(loc=8, ncol=2, bbox_to_anchor=[0.5, -0.1])
    
    
    
    ax.tick_params(axis='x', pad=-10)
    
    st.pyplot(fig)
    

# Row 3
def market_value(trans_df, player_dim, player_id, club_color, player_id2="", club_color2=""):
        
    player = player_dim[player_dim['fbref']==player_id]
    df = trans_df.merge(player.loc[:,'transfermarkt'], how='inner', left_on='id', right_on='transfermarkt')
    
    # Values
    x = df['date']
    y = df['value']
    
    # Formatters
    # x-axis
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    x_formatter = mdates.ConciseDateFormatter(locator)
    
    # y-axis
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)
    
    def mixed(x, pos):
        return '%1.1fM' % (x * 1e-6)
    
    def thousands(x, pos):
        return '%1.0fk' % (x * 1e-3)
    
    if y.median() >= 1000000:
        y_formatter = FuncFormatter(millions)
    elif y.max() >= 1000000:
        y_formatter = FuncFormatter(mixed)
    else:
        y_formatter = FuncFormatter(thousands)
        
    # Plot figure
    fig, ax = plt.subplots()
    ax.fill_between(x, y, color=club_color, alpha=0.3)
    ax.plot(x, y, color=club_color)
    
    if player_id2 != "":
        player = player_dim[player_dim['fbref']==player_id2]
        df2 = trans_df.merge(player.loc[:,'transfermarkt'], how='inner', left_on='id', right_on='transfermarkt')
        
        x2 = df2['date']
        y2 = df2['value']
        
        ax.fill_between(x2, y2, color=club_color2, alpha=0.3)
        ax.plot(x2, y2, color=club_color2)
        
        x = pd.concat([x,x2])
    
    ax.set_facecolor('w')
    ax.set_xlim(xmin=x.min(), xmax=x.max())
    ax.set_ylim(ymin=0)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    
    plt.title("Market Value")

    st.pyplot(fig)


def lollipop_chart(percentiles, p90, club_color, percentiles2="", p90_2="", club_color2=""):
    
    
    cols = ['goals', 'assists', 'xG', 'shots', 'key_passes', 'through_balls',
            'crosses', 'into_final_third', 'dribble_success',
            'touches_attacking_pen', 'dribble_progressive_distance', 'fouled',
            'dispossessed', 'pressures', 'tackles', 'interceptions', 'recoveries',
            'xG/shot', 'passing%', 'aerial%']
    
    percentiles = percentiles.loc[:,cols]
    p90 = p90[cols]
    
    
    percentiles = percentiles.rename(columns={'key_passes' : 'key passes',
                                              'through_balls' : 'through balls',
                                              'into_final_third' : 'pass into final 1/3',
                                              'dribble_success' : 'dribbles',
                                              'touches_attacking_pen' : 'touches in box',
                                              'dribble_progressive_distance' : 'prog dribble dist'})
    
    x = percentiles.columns
    y = percentiles.iloc[0,:].multiply(100)
    
    
    fig, ax = plt.subplots()
    
    
    if isinstance(percentiles2, pd.DataFrame):
        
        percentiles2 = percentiles2.loc[:,cols]
        p90_2 = p90_2[cols]
        
        
        percentiles2 = percentiles2.rename(columns={'key_passes' : 'key passes',
                                                    'through_balls' : 'through balls',
                                                    'into_final_third' : 'pass into final 1/3',
                                                    'dribble_success' : 'dribbles',
                                                    'touches_attacking_pen' : 'touches in box',
                                                    'dribble_progressive_distance' : 'prog dribble dist'})
        
        y2 = percentiles2.iloc[0,:].multiply(100)
        
        df = pd.concat([y, y2], axis=1)
        df['min'] = df.min(axis=1)
        df['max'] = df.max(axis=1)
        
        ind = range(1,len(percentiles.columns)+1)
        plt.hlines(ind, xmin=df['min'], xmax=df['max'], color='grey')
        plt.scatter(y, ind, color=club_color, label='player1')       
        plt.scatter(y2, ind, color=club_color2, label='player2')
        
        
        
    else:
        ind = range(1,len(percentiles.columns)+1)
        plt.hlines(ind, xmin=0, xmax=y, color=club_color, label='player1')
        plt.plot(y, ind, "o", markerfacecolor=club_color)
       
        
        for i, v in enumerate(y):
            if i < 18:
                plt.text(v + 3, i + .75, str(round(p90[i],2)))
            else:
                plt.text(v + 3, i + .75, str(round(p90[i]*100,1))+'%')
    
    
    plt.yticks(ind, x)
    
    ax.set_yticklabels(x, minor=False, fontsize='small')
    ax.set_xlim(0,100)
    
    txt = 'data labels are non-percentile p90 stats'
    plt.figtext(.1, 0, txt, fontstyle='italic')
    plt.title('p90 Percentiles')
    
    st.pyplot(fig)  
    


# Row 4
def match_log(v_player_match_stats_fact, match_dim, player_id, pos_group):
    
    v_player_match_stats_fact = v_player_match_stats_fact[v_player_match_stats_fact['player_id']==player_id]
    
    # v_player_match_stats_fact['xG'] = v_player_match_stats_fact['xG'].round(2)
    
    
    log_base_cols = ['date', 'opponent', 'league', 'position', 'minutes', 'goals', 'assists']
    log_attack_cols = ['xG', 'shots', 'key_passes', 'passing%','dribble_success', 'touches', 'touches_attacking_pen', 'tkl+int']
    log_wm_cols = ['passing%', 'key_passes', 'through_balls', 'crosses', 'tkl+int', 'dispossessed', 'dribble_success', 'recoveries']
    log_cm_cols = ['passing%', 'key_passes', 'through_balls', 'tackles', 'interceptions', 'dispossessed', 'fouls', 'pass_progressive_distance']
    log_fb_cols = ['tackles', 'interceptions', 'passing%', 'key_passes', 'crosses', 'dribble_success', 'fouls', 'recoveries']
    log_cb_cols = ['passing%', 'tackles', 'interceptions', 'blocks', 'clearances', 'fouls', 'aerials_won', 'pass_progressive_distance']
    
    pos_cols = {
        'ST' : log_attack_cols,
        'Winger/AM' : log_attack_cols,
        'WM' : log_wm_cols,
        'CM/DM' : log_cm_cols,
        'FB' : log_fb_cols,
        'CB' : log_cb_cols
        }
    cols = log_base_cols + pos_cols.get(pos_group)
    
    df = match_dim.merge(v_player_match_stats_fact, how='inner', left_on='id', right_on='match_id').drop(columns={'id'})
    
    df['opponent'] = np.where(df['team_id']==df['id_x'], df['team_y'], df['team_x'])
    df['passing%'] = df['passes_completed'] / df['passes_attempted']
    df['tkl+int'] = df['tackles'] + df['interceptions']
    
    
    df = df.loc[:,cols]
    
    for col in df.columns:
        if col not in ['date', 'opponent', 'league', 'position', 'xG', 'passing%']:
            df[col] = df[col].astype(int)
    
    df = df.rename(columns={'position' : 'pos',
                            'minutes' : 'mins',
                            'goals' : 'gls',
                            'assists' : 'ast',
                            'key_passes' : 'kp',
                            'dribble_success' : 'dribbles',
                            'touches_attacking_pen' : 'touches in pen',
                            'aerials_won' : 'aerials won',
                            'pass_progressive_distance' : 'pass progressive distance'})
    
    
    df = df.sort_values('date', ascending=False)
    
    return df.set_index('date')


#~~~~~VIEWS~~~~~

# View
def view(name):
    
    if name=='Player':
        player_view()
    elif name=='Player Comparison':
        comparison_view()

# Player
def player_view():
    
    # row2 (Demographic, KPIs, Radar)
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4, \
        row2_4, row2_spacer_5 = st.beta_columns((.15, .5, .005, .75, .005, .5, .005, 1, .15))
    
    with row2_1:
        st.image(headshot)
    
    with row2_2:
        st.text("Name: {0:s}".format(demo[0]))
        st.text("Position: {0:s}".format(demo[1]))
        st.text("Born: {0:s}".format(str(demo[2].strftime('%d-%b-%Y')) + " (" + str(demo[3]) + ")"))
        st.text("Birth Place: {0:s}".format(demo[4]))
        st.text("Nationality: {0:s}".format(demo[5]))
        st.text("Height: {0:s}m".format(str(demo[6])))
        st.text("Foot: {0:s}".format(str(demo[7])))
        st.text("Club: {0:s}".format(demo[8]))
        try:
            st.text("Contracted Until: {0:s}".format(str(demo[9].strftime('%d-%b-%Y'))))
        except:
            st.text("Contracted Until: unknown")
        st.text("Market Value: \u20ac{0:s}".format(demo[10]))
    
    with row2_3:
        try:
            st.text("Minutes: {0:.0f}".format(kpi[0]))
            st.text("G: {0:.0f}".format(kpi[1]))
            st.text("A: {0:.0f}".format(kpi[2]))
            st.text("xG: {0:.1f}".format(kpi[3]))
            st.text("SCA: {0:.0f}".format(kpi[4]))
        except:
            st.write("")
    
    with row2_4:
        try:
            radar(p90[0], pos_group, club_color)
        except:
            st.write("Player does not mean minimum number of minutes based on selected timeframe")
    
            
    
    # row 3 (Market Value, Lollipop)
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.15, 1, .005, 1, .15))
    
    with row3_1:
        st.subheader("")
        market_value(trans_mv_fact, player_dim, player_id, club_color)
        
    with row3_2:
        st.subheader("")
        try:
            lollipop_chart(p90[0], p90[1], club_color)
        except:
            st.write("Player does not mean minimum number of minutes based on selected timeframe")
            
            
    
    # row 4 (Match Log)
    row4_spacer1, row4_1, row4_spacer2 = st.beta_columns((.1, 3.2, .1))
    
    with row4_1:
        st.subheader("Match Log")
        st.dataframe(match_log(v_player_match_stats_fact_fil, match_dim_fil, player_id, pos_group).style.format({"xG": "{:.1f}",
                                                                                                          "passing%" : "{:.1%}"}))
    


def comparison_view():
    
    # row2 (Demographic, KPIs, Radar)
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer4, \
        row2_4, row2_spacer_5 = st.beta_columns((.15, .6, .005, .6, .005, .55, .005, 1, .15))
    
    with row2_1:
        st.image(headshot)
        st.text("Name: {0:s}".format(demo[0]))
        st.text("Position: {0:s}".format(demo[1]))
        st.text("Born: {0:s}".format(str(demo[2].strftime('%d-%b-%Y')) + " (" + str(demo[3]) + ")"))
        st.text("Birth Place: {0:s}".format(demo[4]))
        st.text("Nationality: {0:s}".format(demo[5]))
        st.text("Height: {0:s}m".format(str(demo[6])))
        st.text("Foot: {0:s}".format(str(demo[7])))
        st.text("Club: {0:s}".format(demo[8]))
        try:
            st.text("Contracted Until: {0:s}".format(str(demo[9].strftime('%d-%b-%Y'))))
        except:
            st.text("Contracted Until: unknown")
        st.text("Market Value: \u20ac{0:s}".format(demo[10]))
    
    
    with row2_2:
        st.image(headshot2)
        st.text("{0:s}".format(demo2[0]))
        st.text("{0:s}".format(demo2[1]))
        st.text("{0:s}".format(str(demo2[2].strftime('%d-%b-%Y')) + " (" + str(demo2[3]) + ")"))
        st.text("{0:s}".format(demo2[4]))
        st.text("{0:s}".format(demo2[5]))
        st.text("{0:s}m".format(str(demo2[6])))
        st.text("{0:s}".format(str(demo2[7])))
        st.text("{0:s}".format(demo2[8]))
        try:
            st.text("{0:s}".format(str(demo2[9].strftime('%d-%b-%Y'))))
        except:
            st.text("unknown")
        st.text("\u20ac{0:s}".format(demo2[10]))
    
    with row2_3:
        try:
            st.text("Minutes: {0:.0f} vs. {1:.0f}".format(kpi[0], kpi2[0]))
            st.text("G: {0:.0f} vs. {1:.0f}".format(kpi[1], kpi2[1]))
            st.text("A: {0:.0f} vs. {1:.0f}".format(kpi[2], kpi2[2]))
            st.text("xG: {0:.1f} vs. {1:.1f}".format(kpi[3], kpi2[3]))
            st.text("SCA: {0:.0f} vs. {1:.0f}".format(kpi[4], kpi2[4]))
        except:
            st.write("")
    
    with row2_4:
        try:
            radar(p90[0], pos_group, club_color, p90_2[0], club_color2)
        except:
            st.write("Player does not mean minimum number of minutes based on selected timeframe")
            
            
    # row 3 (Market Value, Lollipop)
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.15, 1, .005, 1, .15))
    
    with row3_1:
    #     st.subheader("")
        market_value(trans_mv_fact, player_dim, player_id, club_color, player_id2, club_color2)
        
    with row3_2:
        st.subheader("")
        try:
            lollipop_chart(p90[0], p90[1], club_color, p90_2[0], p90_2[1], club_color2)
        except:
            st.write("Player does not mean minimum number of minutes based on selected timeframe")











#~~~~~DEFAULTS~~~~~
player_dim, team_dim, match_dim, v_player_match_stats_fact, trans_mv_fact, player_list, season_list = load_data()

# Inputs
player_id = '4c370d81'
pos_group = 'ST'
p_color_club = '#D10022'
s_color_club = '#00A499'
club_color = p_color_club if p_color_club.upper() not in ('#FFFFFF', '#FCFCFC', '#FAF7F7') else s_color_club
selected_season = '20/21'
selected_mins = 200

# Call functions
headshot = 'https://fbref.com/req/202005121/images/headshots/' + player_id + '_2018.jpg'
demo = demographic(player_dim, player_id)
match_dim_fil, v_player_match_stats_fact_fil = filter_data(match_dim, v_player_match_stats_fact, selected_season)
kpi = kpis(v_player_match_stats_fact_fil, player_id)
p90 = percentiles(v_player_match_stats_fact_fil, player_dim, player_id, pos_group, selected_mins)



#~~~~~ROW1 (HEADER)~~~~~
row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((.1, 2, 1, 1, .1))

row1_1.title('Soccer Dashboard')

with row1_2:
    st.write('')
    row1_2.subheader(
    'A Web App by [Ian Shepherd](https://github.com/ian-shepherd)') 




#~~~~~SIDEBAR~~~~~

# Inputs
selected_view = st.sidebar.radio('View', ('Player', 'Player Comparison'))

if selected_view == 'Player':
    selected_player = st.sidebar.selectbox("Select a player", player_list, player_list.index("Roberto Firmino (Liverpool FC-4c370d81)"))
elif selected_view == 'Player Comparison':
    selected_player = st.sidebar.selectbox("Select a player", player_list, player_list.index("Roberto Firmino (Liverpool FC-4c370d81)"), key="comp_player1")
    selected_player2 = st.sidebar.selectbox("Select a player", player_list, player_list.index("Gabriel Jesus (Manchester City-b66315ae)"), key="comp_player2")
    st.sidebar.write("""
                     *Percentiles are based on each player's position. Consequently, when 
                     comparring players in different positions it may lead to "strange" results.
                     """)
selected_season = st.sidebar.multiselect('Seasons', options=season_list, default=['20/21'])
selected_mins = st.sidebar.number_input("Minimum number of minutes", min_value=200, value=200)    


# Apply filters
if st.sidebar.button('Apply'):
    # Inputs
    player_id = player_dim[player_dim['player_slicer']==selected_player]['fbref'].iloc[0]
    pos_group = player_dim[player_dim['fbref']==player_id]['pos_group'].iloc[0]
    club = player_dim[player_dim['fbref']==player_id]['club'].iloc[0]
    p_color_club = team_dim[team_dim['transfermarkt_name']==club]['primary_color'].iloc[0]
    s_color_club = team_dim[team_dim['transfermarkt_name']==club]['secondary_color'].iloc[0]
    club_color = p_color_club if p_color_club.upper() not in ('#FFFFFF', '#FCFCFC', '#FAF7F7') else s_color_club
        
    # Call functions
    headshot = 'https://fbref.com/req/202005121/images/headshots/' + player_id + '_2018.jpg'
    demo = demographic(player_dim, player_id)

    # Filter data
    match_dim_fil, v_player_match_stats_fact_fil = filter_data(match_dim, v_player_match_stats_fact, selected_season)
    kpi = kpis(v_player_match_stats_fact_fil, player_id)
    p90 = percentiles(v_player_match_stats_fact_fil, player_dim, player_id, pos_group, selected_mins)
    
    
    # player2
    try:
        player_id2 = player_dim[player_dim['player_slicer']==selected_player2]['fbref'].iloc[0]
        pos_group2 = player_dim[player_dim['fbref']==player_id2]['pos_group'].iloc[0]
        club2 = player_dim[player_dim['fbref']==player_id2]['club'].iloc[0]
        p_color_club2 = team_dim[team_dim['transfermarkt_name']==club2]['primary_color'].iloc[0]
        s_color_club2 = team_dim[team_dim['transfermarkt_name']==club2]['secondary_color'].iloc[0]
        if p_color_club2.upper() not in ('#FFFFFF', '#FCFCFC', '#FAF7F7') and p_color_club2.upper() != club_color.upper():
            club_color2 = p_color_club2
        elif p_color_club2.upper() in ('#FFFFFF', '#FCFCFC', '#FAF7F7') and s_color_club2.upper() != club_color.upper():
            club_color2 = s_color_club2
        elif isinstance(team_dim[team_dim['transfermarkt_name']==club2]['alternate_color'].iloc[0], float):
            club_color2 = '#34EB83'
        else:
            club_color2 = team_dim[team_dim['transfermarkt_name']==club2]['alternate_color'].iloc[0]
            
        if club_color == club_color2:
            club_color2 = '#34EB83'

        
        # call function
        headshot2 = 'https://fbref.com/req/202005121/images/headshots/' + player_id2 + '_2018.jpg'
        demo2 = demographic(player_dim, player_id2)
        
        # filter data
        match_dim_fil2, v_player_match_stats_fact_fil2 = filter_data(match_dim, v_player_match_stats_fact, selected_season)
        kpi2 = kpis(v_player_match_stats_fact_fil2, player_id2)
        p90_2 = percentiles(v_player_match_stats_fact_fil2, player_dim, player_id2, pos_group2, selected_mins)
        
    except Exception:
        pass
    
    
    
    
    view(selected_view)
 
    



#~~~~~ROW 5 (Additional Info Expander)~~~~~
row5_spacer1, row5_1, row5_spacer2 = st.beta_columns((.1, 3.2, .1))

with row5_1:
    st.markdown('___')
    about = st.beta_expander('About/Additional Info')
    with about:
        '''
        This app was built primarily using [fbref] (https://fbref.com/) and [Transfermarkt] (https://transfermarkt.com/), 
        both of which do a great job providing a wealth of data. I focused exclusively on the Big 5 leagues, Champions League, 
        Europa Leage, and MLS due to the availability of [StatsBomb] (https://statsbomb.com/) data. Due to the slow changing nature
        of Transfermarkt data I only update that data periodically. I try to update the fbref data more frequently as matches
        occur but plan to refresh that data at least once a week. Aditionally, any players with less than 500 minutes of play
        in the above competitions are not guaranteed to show up here as I have to add them to a translation table that matches
        fbref and Transferamrkt IDs. As you can imagine it is a tedious task. I will try and do bulk updates to add more players
        beyond that threshold as time permits.
        
        As a disclaimer this is the first app I have built so it is far from perfect. Consequently, it is not mobile compatible 
        and looks much better on a wide screen. Please refer to my [GitHub] (https://github.com/ian-shepherd) for future roadmap.
        
        '''
    
