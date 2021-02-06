#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Jan 30 2021
#Last updated Fri Feb 5 2021

#@author: ishepher

#Input: csvs
#Output: streamlit web app 
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import seaborn as sns
from math import pi


_lock = RendererAgg.lock
plt.style.use('seaborn')
sns.set_style(style='white')

# Folder paths
dataFolder = 'https://github.com/ian-shepherd/soccer/blob/main/Data/'

# Use the full page instead of a narrow central column
st.set_page_config(page_title='Soccer Dashboard',
                   page_icon='https://raw.githubusercontent.com/papagorgio23/Python101/master/newlogo.png',
                   layout="wide")



# Import data
@st.cache(allow_output_mutation=True)
def load_data():
    
    # player dim
    player_dim = pd.read_csv(dataFolder + 'player_dim.csv' + '?raw=true',
                             usecols=['fbref', 'transfermarkt', 'player_name', 'pos_group', 'born', 'nationality', 'height', 'club', 'contracted', 'mv'])
    player_dim['born'] = pd.to_datetime(player_dim['born']).dt.date
    player_dim['contracted'] = pd.to_datetime(player_dim['contracted']).dt.date
    player_dim = player_dim[player_dim['club'].notnull()]
    player_dim = player_dim[player_dim['pos_group']!='GK']
    player_dim['player_slicer'] = player_dim['player_name'] + ' (' + player_dim['club'] + '-' + player_dim['fbref'] +')'
    
    # team_dim
    team_dim = pd.read_csv(dataFolder + 'team_dim.csv' + '?raw=true', usecols=['fbref', 'transfermarkt_name', 'primary_color', 'secondary_color'])
    
    # match_dim
    match_dim = pd.read_csv(dataFolder + 'match_dim.csv' + '?raw=true')
    match_dim['date'] = pd.to_datetime(match_dim['date']).dt.date
    
    # match_stats_fact
    matchday_stats_fact = pd.read_csv(dataFolder + 'matchday_stats_fact.csv' + '?raw=true', usecols=['match_id', 'possession_x', 'possession_y'])
    matchday_stats_fact = matchday_stats_fact.merge(match_dim.loc[:,['id', 'id_x', 'id_y']], how='inner', left_on='match_id', right_on='id').drop(columns=['id'])
    matchday_stats_fact_x = matchday_stats_fact.loc[:,['match_id', 'id_x', 'possession_x']]
    matchday_stats_fact_x.columns = ['match_id', 'team_id', 'possession']
    matchday_stats_fact_y = matchday_stats_fact.loc[:,['match_id', 'id_y', 'possession_y']]
    matchday_stats_fact_y.columns = ['match_id', 'team_id', 'possession']
    matchday_stats_fact = pd.concat([matchday_stats_fact_x, matchday_stats_fact_y], ignore_index=True)
                                                    
    
    
    # player_match_stats_fact
    player_match_stats_fact = pd.read_csv(dataFolder + 'player_match_stats_fact.csv' + '?raw=true', 
                                          usecols=['player_match_key', 'match_key', 'match_id', 'team_id', 'player_id', 'position',
                                                   'minutes', 'goals', 'assists', 'pk', 'xG', 'shots', 'shots_on_target', 'shot_creating_actions',
                                                   'passes_attempted', 'passes_completed', 'dribble_progressive_distance', 'dribble_success'])
    
    # player_defense_match_stats_fact
    player_defense_match_stats_fact = pd.read_csv(dataFolder + 'player_defense_match_stats_fact.csv' + '?raw=true',
                                              usecols=['player_match_key', 'pressures', 'tackles', 'interceptions', 'blocks', 'clearances', 'dribbled_past'])
    
    # player_passing_match_stats_fact
    player_passing_match_stats_fact = pd.read_csv(dataFolder + 'player_passing_match_stats_fact.csv' + '?raw=true',
                                                  usecols=['player_match_key', 'key_passes', 'into_final_third', 'progressive_distance'])
    
    # player_passing_type_match_stats_fact
    player_passing_type_match_stats_fact = pd.read_csv(dataFolder + 'player_passing_type_match_stats_fact.csv' + '?raw=true',
                                                       usecols=['player_match_key', 'crosses', 'through_balls'])
    player_passing_match_stats_fact = player_passing_match_stats_fact.rename(columns={'progressive_distance' : 'pass_progressive_distance'})
    
    # player_possession_match_stats_fact
    player_possession_match_stats_fact = pd.read_csv(dataFolder + 'player_possession_match_stats_fact.csv' + '?raw=true',
                                                     usecols=['player_match_key', 'touches', 'dispossessed', 'touches_attacking_pen'])
    
    # player_misc_match_stats_fact
    player_misc_match_stats_fact = pd.read_csv(dataFolder + 'player_misc_match_stats_fact.csv' + '?raw=true',
                                               usecols=['player_match_key', 'fouled', 'fouls', 'aerials_won', 'aerials_lost', 'recoveries'])
    
    
    # Player stats view
    v_player_match_stats_fact = player_match_stats_fact.merge(player_defense_match_stats_fact, how='inner', on='player_match_key')
    v_player_match_stats_fact = v_player_match_stats_fact.merge(player_passing_match_stats_fact, how='inner', on='player_match_key')
    v_player_match_stats_fact = v_player_match_stats_fact.merge(player_passing_type_match_stats_fact, how='inner', on='player_match_key')
    v_player_match_stats_fact = v_player_match_stats_fact.merge(player_possession_match_stats_fact, how='inner', on='player_match_key')
    v_player_match_stats_fact = v_player_match_stats_fact.merge(player_misc_match_stats_fact, how='inner', on='player_match_key')
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
    trans_mv_fact = pd.read_csv(dataFolder + 'trans_mv_fact.csv' + '?raw=true')
    trans_mv_fact['date'] = pd.to_datetime(trans_mv_fact['date']).dt.date
    
    
    # lists
    player_list = player_dim['player_slicer'].tolist()
    season_list = match_dim['season'].unique().tolist()
    min_date = match_dim['date'].min()
    max_date = match_dim['date'].max()
    
    
    return player_dim, team_dim, match_dim, player_match_stats_fact, player_defense_match_stats_fact, player_passing_match_stats_fact, \
            player_passing_type_match_stats_fact, player_possession_match_stats_fact, player_misc_match_stats_fact, \
            v_player_match_stats_fact, trans_mv_fact, player_list, season_list, min_date, max_date


player_dim, team_dim, match_dim, player_match_stats_fact, player_defense_match_stats_fact, player_passing_match_stats_fact, \
    player_passing_type_match_stats_fact, player_possession_match_stats_fact, player_misc_match_stats_fact, \
    v_player_match_stats_fact, trans_mv_fact, player_list, season_list, min_date, max_date = load_data()




@st.cache(allow_output_mutation=True)
def filter_data(match_dim, player_match_stats_fact, v_player_match_stats_fact, \
                date_type, selected_seasons=season_list, selected_min=min_date, selected_max=max_date):
    
    selected_seasons = [selected_seasons] if isinstance(selected_seasons, str) else selected_seasons
    
    if date_type == 'Season':
        match_dim = match_dim[match_dim['season'].isin(selected_seasons)]
        
    
    else:
        match_dim = match_dim[(match_dim['date']>=selected_min) & (match_dim['date']<=selected_max)]
        
    player_match_stats_fact = player_match_stats_fact.merge(match_dim.loc[:,['id']], how='inner', left_on='match_id', right_on='id').drop(columns=['id'])
    v_player_match_stats_fact = v_player_match_stats_fact.merge(match_dim.loc[:,['id']], how='inner', left_on='match_id', right_on='id').drop(columns=['id'])
    
    
    return match_dim, player_match_stats_fact, v_player_match_stats_fact






#~~~~~ROW1 (HEADER)~~~~~

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns((.1, 2, 1.5, 1, .1))


row1_1.title('Soccer Dashboard')



with row1_2:
    st.write('')
    row1_2.subheader(
    'A Web App by [Ian Shepherd](https://github.com/ian-shepherd)')




#~~~~~ROW 2 (FILTERS)~~~~~
row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3, row2_3, row2_spacer_4, row2_4, row2_spacer5 = st.beta_columns((.2, 2, .1, .5, .1, 2, .1, .75, 1.5))
  





with row2_1:
    selected_player = st.selectbox("Select a player", player_list)
    player_id = player_dim[player_dim['player_slicer']==selected_player]['fbref'].iloc[0]
    pos_group = player_dim[player_dim['fbref']==player_id]['pos_group'].iloc[0]
    club = player_dim[player_dim['fbref']==player_id]['club'].iloc[0]
    p_color_club = team_dim[team_dim['transfermarkt_name']==club]['primary_color'].iloc[0]
    s_color_club = team_dim[team_dim['transfermarkt_name']==club]['secondary_color'].iloc[0]
    club_color = p_color_club if p_color_club not in ('#FFFFFF', '#FCFCFC') else s_color_club
    
    
    
with row2_2:
    date_type = st.radio("Filter type", ('Season', 'Dates'))
    
with row2_3:
    if date_type == 'Season':
        selected_season = st.multiselect('Seasons', options=season_list, default='20/21')
        match_dim, player_match_stats_fact, v_player_match_stats_fact = filter_data(match_dim, player_match_stats_fact, v_player_match_stats_fact, date_type, selected_season)
        
    else:
        date_delta = (max_date - min_date).days
        date_range = pd.date_range(min_date, periods = date_delta + 1).date.tolist()
        start_date, end_date = st.select_slider("Date Range", options=date_range, value=(dt.date(2020,9,12),max_date))
        match_dim, player_match_stats_fact, v_player_match_stats_fact = filter_data(match_dim, player_match_stats_fact, v_player_match_stats_fact, date_type, selected_min=start_date, selected_max=end_date)
    
with row2_4:
    selected_mins = st.number_input("Minimum number of minutes", min_value=200, value=200)

st.text("")
st.text("")




#~~~~~ROW 3 (Demographic, KPIs, Radar)~~~~~
row3_spacer1, row3_1, row3_spacer2, row3_2, row3_3, row3_4, row3_5, \
    row3_6, row3_spacer7 = st.beta_columns((.15, 1.5, .005, 0.5, 0.5, 0.5, 0.5,  0.5, .4))


def radar(df, player_dim, player_id, pos_group, club_color, min_filter):
    
    
    
    # Create copies of data
    playerStatsDF = df.copy()
    playerStatsDF = playerStatsDF.drop(columns=['player_match_key'])
    
    # Filter position group
    player_dim = player_dim[player_dim['pos_group']==pos_group]
    playerStatsDF = playerStatsDF.merge(player_dim.loc[:,['fbref']], how='inner', left_on='player_id', right_on='fbref').drop(columns=['fbref'])
    
    # Filter minimum minutes
    players = playerStatsDF.loc[:,['player_id', 'minutes']]
    players = players.groupby(['player_id']).sum()
    players = players[players['minutes']>=min_filter]
    players = players.drop(columns=['minutes'])       
    
    # Aggregate per 90
    df = players.merge(playerStatsDF, how='inner', on=['player_id']).drop(columns=['match_key']) 
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
    
    # Get percentiles
    for col in df.columns:
        df.loc[:,col] = df[col].rank(pct=True)
    
    # Reverse percentiles where high = bad
    df['dispossessed'] = 1 - df['dispossessed']
    df['fouls'] = 1 - df['fouls']
    df['dribbled_past'] = 1 - df['dribbled_past']
    df['pAdjDribbled_Past'] = 1 - df['pAdjDribbled_Past']
    
    # Filter for player
    df = df.reset_index()
    df = df[df['player_id']==player_id]
    
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
        'FWD/AM' : attack_cols,
        'WM' : wm_cols,
        'CM/DM' : cm_cols,
        'FB' : fb_cols,
        'CB' : cb_cols
        }
    cols = pos_cols.get(pos_group)
    df = df.loc[:, cols]
    
    # Rename stats
    df = df.rename(columns={'dribble_success' : 'successful\ndribbles'})
    df = df.rename(columns={'through_balls' : 'through balls'})
    df = df.rename(columns={'key_passes' : 'key passes'})
    df = df.rename(columns={'pass_progressive_distance' : 'pass progressive\ndistance'})
    df = df.rename(columns={'goal_contributions' : 'G+A'})
    df = df.rename(columns={'pAdjDribbled_Past' : 'pAdjDribbled\npast'})
    df = df.rename(columns={'dribbled_past' : 'dribbled past'})
    df = df.rename(columns={'aerials_won' : 'aerials won'})
    df = df.rename(columns={'into_final_third' : 'passes into\nfinal third'})
    
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
    plt.yticks([.2,.4, .6, .8, 1], ["0.2","0.4","0.6", "0.8"], color="grey", size=7)
    plt.ylim(0,1)
    
    # Add data
    values = df.values.flatten().tolist()
    values += values[:1]
    
    ax.plot(angles, values, color=club_color, linewidth=1, linestyle='solid')
    ax.fill(angles, values, color=club_color, alpha=0.25)
       
    ax.tick_params(axis='x', pad=-10)
    
    st.pyplot(fig)

    
def demographic(df, player_id):
    
    df = df[df['fbref']==player_id]
    
    born = df.loc[:,'born'].iloc[0]
    nationality = df.loc[:,'nationality'].iloc[0]
    height = df.loc[:,'height'].iloc[0]
    position = df.loc[:,'pos_group'].iloc[0]
    market_value = df.loc[:,'mv'].iloc[0]
    contract_until = df.loc[:,'contracted'].iloc[0]
    age = relativedelta(dt.date.today(), born).years
    mv = (str(market_value.astype(float)/1000000) + 'm' if market_value>=1000000 else str(int(market_value.astype(float)/1000)) + "k")
    
    
    
    return df, born, age, nationality, height, position, mv, contract_until

def kpis(df, player_id):
    
    df = player_match_stats_fact[player_match_stats_fact['player_id']==player_id]
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

def p90_kpi(df, player_id):
    
    
    df = df[df['player_id']==player_id]
    
    cols = ['player_id', 'minutes', 'goals', 'assists', 'xG', 'shots',
            'key_passes', 'passes_completed', 'passes_attempted', 'through_balls', 'crosses', 'into_final_third',
            'dribble_success', 'touches_attacking_pen', 'dribble_progressive_distance', 'fouled', 'dispossessed',
            'pressures', 'tackles', 'interceptions', 'recoveries', 'aerials_won', 'aerials_lost']
    
    df = df.loc[:,cols]
    df = df.groupby(['player_id']).sum()
    mask = ~(df.columns.isin(['minutes']))
    agg_cols = df.columns[mask].tolist()
    df.loc[:, agg_cols] = df.loc[:, agg_cols].div(df['minutes'], axis=0) * 90
    df['xG/shot'] = df['xG'] / df['shots']
    df['passing%'] = df['passes_completed'] / df['passes_attempted']
    df['aerial%'] = df['aerials_won'] / (df['aerials_won'] + df['aerials_lost'])
    df = df.drop(columns=['minutes', 'passes_completed', 'passes_attempted', 'aerials_won', 'aerials_lost'])
    
    
    gls = df['goals'].iloc[0]
    ast = df['assists'].iloc[0]
    xg = df['xG'].iloc[0]
    shots = df['shots'].iloc[0]
    xg_shot = df['xG/shot'].iloc[0]
    
    key_passes = df['key_passes'].iloc[0]
    pass_per = df['passing%'].iloc[0]
    through_balls = df['through_balls'].iloc[0]
    crosses = df['crosses'].iloc[0]
    pass_third = df['into_final_third'].iloc[0]
    
    dribble = df['dribble_success'].iloc[0]
    touch_pen = df['touches_attacking_pen'].iloc[0]
    drib_prog_dist = df['dribble_progressive_distance'].iloc[0]
    fouled = df['fouled'].iloc[0]
    dispossessed = df['dispossessed'].iloc[0]
    
    pressures = df['pressures'].iloc[0]
    tkl = df['tackles'].iloc[0]
    inter = df['interceptions'].iloc[0]
    recoveries = df['recoveries'].iloc[0]
    aerial_per = df['aerial%'].iloc[0]
    
    
    df1 = df.loc[:,['goals', 'assists', 'xG', 'shots', 'xG/shot']]
    df2 = df.loc[:,['key_passes', 'passing%', 'through_balls', 'crosses', 'into_final_third']]
    df2 = df2.rename(columns={'key_passes' : 'key passes',
                              'through_balls' : 'through balls',
                              'into_final_third' : 'passed into final 1/3'})
    df3 = df.loc[:,['dribble_success', 'touches_attacking_pen', 'dribble_progressive_distance', 'fouled', 'dispossessed']]
    df4 = df.loc[:,['pressures', 'tackles', 'interceptions', 'recoveries', 'aerial%']]
    
    
    return gls, ast, xg, shots, xg_shot, \
        key_passes, pass_per, through_balls, crosses, pass_third, \
        dribble, touch_pen, drib_prog_dist, fouled, dispossessed, \
        pressures, tkl, inter, recoveries, aerial_per, \
        df1, df2, df3, df4

demo = demographic(player_dim, player_id)
kpi = kpis(player_match_stats_fact, player_id)
p90 = p90_kpi(v_player_match_stats_fact, player_id)





with row3_1, _lock:
    try:
        radar(v_player_match_stats_fact, player_dim, player_id, pos_group, club_color, selected_mins)
    except:
        st.write("Player does not mean minimum number of minutes based on selected timeframe")
    
with row3_2:
    st.write("")
    st.write("")
    st.text("{0:s}\nborn".format(str(demo[1].strftime('%d-%b-%Y')) + " (" + str(demo[2]) + ")"))
    st.text("")
    st.text("{0:.0f}\nminutes".format(kpi[0]))
    st.subheader("p90")
    st.text("{0:.2f}\ngoals".format(p90[0]))
    st.text("{0:.2f}\nkey passes".format(p90[5]))
    st.text("{0:.2f}\ndribbles".format(p90[10]))
    st.text("{0:.2f}\npressures".format(p90[15]))
            
with row3_3:
    st.write("")
    st.write("")
    st.text("{0:s}m\nheight".format(str(demo[4])))
    st.text("")
    st.text("{0:.0f}\ngoals".format(kpi[1]))
    st.subheader("")
    st.text("")
    st.text("{0:.2f}\nassists".format(p90[1]))
    st.text("{0:.2%}\npassing%".format(p90[6]))
    st.text("{0:.2f}\ntouches in box".format(p90[11]))
    st.text("{0:.2f}\ntackles".format(p90[16]))
    
with row3_4:
    st.write("")
    st.write("")
    st.text("{0:s}\nnationality".format(str(demo[3])))
    st.text("")
    st.text("{0:.0f}\nassists".format(kpi[2]))
    st.subheader("")
    st.text("")
    st.text("{0:.2f}\nxG".format(p90[2]))
    st.text("{0:.2f}\nthrough balls".format(p90[7]))
    st.text("{0:.2f}\nprog dribble dist".format(p90[12]))
    st.text("{0:.2f}\ninterceptions".format(p90[17]))
with row3_5:
    st.write("")
    st.write("")
    st.text("{0:s}\nposition".format(str(demo[5])))
    st.text("")
    st.text("{0:.1f}\nxG".format(kpi[3]))
    st.subheader("")
    st.text("")
    st.text("{0:.2f}\nshots".format(p90[3]))
    st.text("{0:.2f}\ncrosses".format(p90[8]))
    st.text("{0:.2f}\nfouled".format(p90[13]))
    st.text("{0:.2f}\nrecoveries".format(p90[18]))
with row3_6:
    st.write("")
    st.write("")
    st.text("\u20ac{0:s}\nmarket value".format(demo[6]))
    st.text("")
    st.text("{0:.0f}\nsca".format(kpi[4]))
    st.subheader("")
    st.text("")
    st.text("{0:.2f}\nxG/shot".format(p90[4]))
    st.text("{0:.2f}\npass into final 1/3".format(p90[9]))
    st.text("{0:.2f}\ndispossed".format(p90[14]))
    st.text("{0:.2%}\naerial%".format(p90[19]))





    
    
#~~~~~ROW 4~~~~~
    
row4_spacer1, row4_1, row4_spacer2, row4_2, row4_spacer3 = st.beta_columns((.15, 1.5, .005, 2.75, .4))

def market_value(df, player_dim, player_id, club_color):
        
    player = player_dim[player_dim['fbref']==player_id]
    df = df.merge(player.loc[:,'transfermarkt'], how='inner', left_on='id', right_on='transfermarkt')
    
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
    fig, ax = plt.subplots(1)
    ax.fill_between(x, y, color=club_color, alpha=0.3)
    ax.plot(x, y, color=club_color)
    ax.set_facecolor('w')
    ax.set_xlim(xmin=x.min(), xmax=x.max())
    ax.set_ylim(ymin=0)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(x_formatter)
    ax.yaxis.set_major_formatter(y_formatter)
    
    plt.title("Market Value")

    st.pyplot(fig)
    

def match_log(v_player_match_stats_fact, match_dim, player_id, pos_group):
    
    v_player_match_stats_fact = v_player_match_stats_fact[v_player_match_stats_fact['player_id']==player_id]
        
    
    log_base_cols = ['date', 'opponent', 'position', 'minutes', 'goals', 'assists']
    log_attack_cols = ['xG', 'shots', 'key_passes', 'passing%','dribble_success', 'touches', 'touches_attacking_pen', 'tkl+int']
    log_wm_cols = ['passing%', 'key_passes', 'through_balls', 'crosses', 'tkl+int', 'dispossessed', 'dribble_success', 'recoveries']
    log_cm_cols = ['passing%', 'key_passes', 'through_balls', 'tackles', 'interceptions', 'dispossessed', 'fouls', 'pass_progressive_distance']
    log_fb_cols = ['tackles', 'interceptions', 'passing%', 'key_passes', 'crosses', 'dribble_success', 'fouls', 'recoveries']
    log_cb_cols = ['passing%', 'tackles', 'interceptions', 'blocks', 'clearances', 'fouls', 'aerials_won', 'pass_progressive_distance']
    
    pos_cols = {
        'FWD/AM' : log_attack_cols,
        'WM' : log_wm_cols,
        'CM/DM' : log_cm_cols,
        'FB' : log_fb_cols,
        'CB' : log_cb_cols
        }
    cols = log_base_cols + pos_cols.get(pos_group)
    
    df = match_dim.merge(v_player_match_stats_fact, how='inner', on='match_key')
    
    df['opponent'] = np.where(df['team_id']==df['id_x'], df['team_y'], df['team_x'])
    df['passing%'] = df['passes_completed'] / df['passes_attempted']
    df['tkl+int'] = df['tackles'] + df['interceptions']
    
    
    df = df.loc[:,cols]
    
    for col in df.columns:
        if col not in ['date', 'opponent', 'position', 'xG', 'passing%']:
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



with row4_1, _lock:
    st.subheader("")
    market_value(trans_mv_fact, player_dim, player_id, club_color)



with row4_2:
    st.subheader("Match Log")
    st.dataframe(match_log(v_player_match_stats_fact, match_dim, player_id, pos_group).style.format({"xG": "{:.1f}",
                                                                                                      "passing%" : "{:.1%}"}))
    
    


#~~~~~ROW 5 (ADDITIONAL INFO EXPANDER)~~~~~
row5_spacer1, row5_1, row5_spacer2 = st.beta_columns((.1, 3.2, .1))

with row5_1:
    st.markdown('___')
    about = st.beta_expander('About/Additional Info')
    with about:
        '''
        This app was built primarily using [fbref] (https://fbref.com/) and [Transfermarkt] (https://transfermarkt.com/), 
        both of which do a great job providing a wealth of data. I focused exclusively on the Big 5 leagues, Champions League, 
        and Europa Leage due to the availability of [StatsBomb] (https://statsbomb.com/) data. Due to the slow changing nature
        of Transfermarkt data I only update that data periodically. I try to update the fbref data more frequently as matches
        occur but plan to refresh that data at least once a week. Aditionally, any players with less than 500 minutes of play
        in the above competitions are not guaranteed to show up here as I have to add them to a translation table that matches
        fbref and Transferamrkt IDs. As you can imagine it is a tedious task. I will try and do bulk updates to add more players
        beyond that threshold as time permits.
        
        As a disclaimer this is the first app I have built so it is far from perfect. Consequently, it is not mobile compatible 
        and looks much better on a wide screen. Please refer to my [GitHub] (https://github.com/ian-shepherd/soccer) for future roadmap.
        
        '''