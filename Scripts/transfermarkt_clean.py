#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Jan 23 2021
#Last updated Sat Feb 20 2021

#@author: ishepher

#Sources:
    #transfermarkt
#Input: csvs of metadata, market value, and transfers
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
import pandas as pd
import numpy as np
import datetime as dt

# Folder paths
rootFolder = os.path.dirname(os.path.dirname(__file__))
dataFolder = rootFolder + '/Data/Update/'

# Load data
dfMeta = pd.read_csv(dataFolder + 'raw_transfermarkt_player_meta.csv')
dfMV = pd.read_csv(dataFolder + 'raw_transfermarkt_player_mv.csv')
dfTransfers = pd.read_csv(dataFolder + 'raw_transfermarkt_player_transfers.csv')



#~~~~~CLEAN DATA~~~~~

# Functions
def clean_metadata(df):
    
    # happy birthday
    df['born'] = df['born'].str.replace(' Happy Birthday', '')
    
    # dates
    df['born'] = pd.to_datetime(df['born']).dt.date
    df['joined'] = pd.to_datetime(df['joined'], errors='coerce').dt.date
    df['contracted'] = pd.to_datetime(df['contracted'], errors='coerce').dt.date
    df['update'] = pd.to_datetime(df['update'], errors='coerce').dt.date
    
    # height
    df['height'] = dfMeta['height'].str.replace(',', '.').str.replace('m', '').str.strip()
    df['height'] = dfMeta['height'].astype(float)
    
    # position
    df['position_main'] = np.where(~df['position_main'].isnull(), 
                                   df['position_main'], 
                                   df['position'].str.split(' - ').str[-1])

    
    # market value
    df['mv'] = df['mv'].str.replace('â‚¬','').str.replace('€','')
    df['mult'] = np.where(df['mv'].str[-1] == 'm', 1000000, 1000)
    df['mv'] = df['mv'].str.replace('Th.','').str.replace('m','').str.strip()
    df['mv'] = df['mv'].astype(float) * df['mult']
    df = df.drop(columns=['mult'])
    
    return df


def clean_mv(df):
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    
    return df


def clean_transfers(df):
    
    # dates
    df['date'] = df['date'].str.replace('-','')
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by=['id', 'date']).reset_index(drop=True)
    df['future'] = np.where(df['date'] > dt.date.today(), 'Y', 'N')
    
    # loan
    df['loan'] = np.where(df['fee'].str.contains('loan|Loan'), 'Y', 'N')
    df['loan_fee'] = np.where(df['loan'] == 'N', np.nan, 
                              np.where(df['fee'].str.contains('Loan fee:'), df['fee'],'0'))
    
    # free transfers
    df['free'] = np.where(df['fee'] == 'free transfer', 'Y', 'N')
    
    # multiplier
    df['value_mult'] = np.where(df['value'].str[-1] == 'm', 1000000, 1000)
    df['fee_mult'] = np.where(df['fee'].str[-1] == 'm', 1000000, 1000)
    
    # fee
    substring = ['free transfer', 'loan transfer', 'End of loan', 'draft']
    for s in substring:
        df['fee'] = df['fee'].str.replace(s,'0')
    
    df['value'] = np.where(df['value'].str.contains('-|\?'), np.nan, df['value'])
    df['fee'] = np.where(df['fee'].str.contains('-|\?'), np.nan, df['fee'])
    
    substring = ['Loan fee:', '€', 'm', 'Th.', 'â‚¬']
    for s in substring:
        df['value'] = df['value'].str.replace(s,'')
        df['fee'] = df['fee'].str.replace(s,'')
        df['loan_fee'] = df['loan_fee'].str.replace(s,'')
        
    df['value'] = df['value'].str.strip()
    df['fee'] = df['fee'].str.strip()
    df['loan_fee'] = df['loan_fee'].str.strip()
    
    df['value'] = df['value'].astype(float) * df['value_mult']
    df['fee'] = df['fee'].astype(float) * df['fee_mult']
    df['loan_fee'] = df['loan_fee'].astype(float) * df['fee_mult']
    
    df = df.drop(columns=['value_mult', 'fee_mult'])
    
    
    return df


# Clean data
dfMeta = clean_metadata(dfMeta)
dfMV = clean_mv(dfMV)
dfTransfers = clean_transfers(dfTransfers)


# Export data
dfMeta.to_csv(dataFolder + 'player_metadata.csv', index=False)
dfMV.to_csv(dataFolder + 'player_mv_history.csv', index=False)
dfTransfers.to_csv(dataFolder + 'player_transfer_history.csv', index=False)