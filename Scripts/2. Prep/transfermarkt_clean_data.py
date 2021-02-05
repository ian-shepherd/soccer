#~~~~~~OVERVIEW~~~~~~

# -*- coding: utf-8 -*-

#Created on Sat Jan 23 2021
#Last updated Fri Jan 29 2021

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
rootFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
inputFolder = rootFolder + '/Data/2. Update/1. Raw/transfermarkt/'
outputFolder = rootFolder + '/Data/2. Update/2. Cleaned/transfermarkt/'

# Load data
dfMeta = pd.read_csv(inputFolder + 'transfermarkt_player_meta.csv')
dfMV = pd.read_csv(inputFolder + 'transfermarkt_player_mv.csv')
dfTransfers = pd.read_csv(inputFolder + 'transfermarkt_player_transfers.csv')



#~~~~~CLEAN DATA~~~~~

# Meta
# dates
dfMeta['born'] = pd.to_datetime(dfMeta['born']).dt.date
dfMeta['joined'] = pd.to_datetime(dfMeta['joined'], errors='coerce').dt.date
dfMeta['contracted'] = pd.to_datetime(dfMeta['contracted'], errors='coerce').dt.date
dfMeta['update'] = pd.to_datetime(dfMeta['update'], errors='coerce').dt.date

# height
dfMeta['height'] = dfMeta['height'].str.replace(',', '.').str.replace('m', '').str.strip()
dfMeta['height'] = dfMeta['height'].astype(float)

# market value
dfMeta['mv'] = dfMeta['mv'].str.replace('â‚¬','').str.replace('€','')
dfMeta['mult'] = np.where(dfMeta['mv'].str[-1] == 'm', 1000000, 1000)
dfMeta['mv'] = dfMeta['mv'].str.replace('Th.','').str.replace('m','').str.strip()
dfMeta['mv'] = dfMeta['mv'].astype(float) * dfMeta['mult']
dfMeta = dfMeta.drop(columns=['mult'])


# Market Value
dfMV['date'] = pd.to_datetime(dfMV['date']).dt.date


# Transfers
# dates
dfTransfers['date'] = dfTransfers['date'].str.replace('-','')
dfTransfers['date'] = pd.to_datetime(dfTransfers['date']).dt.date
dfTransfers = dfTransfers.sort_values(by=['id', 'date']).reset_index(drop=True)
dfTransfers['future'] = np.where(dfTransfers['date'] > dt.date.today(), 'Y', 'N')

# loan
dfTransfers['loan'] = np.where(dfTransfers['fee'].str.contains('loan|Loan'), 'Y', 'N')
dfTransfers['loan_fee'] = np.where(dfTransfers['loan'] == 'N', np.nan, 
                                   np.where(dfTransfers['fee'].str.contains('Loan fee:'), dfTransfers['fee'],'0'))

# free transfers
dfTransfers['free'] = np.where(dfTransfers['fee'] == 'free transfer', 'Y', 'N')

# multiplier
dfTransfers['value_mult'] = np.where(dfTransfers['value'].str[-1] == 'm', 1000000, 1000)
dfTransfers['fee_mult'] = np.where(dfTransfers['fee'].str[-1] == 'm', 1000000, 1000)

# fee
substring = ['free transfer', 'loan transfer', 'End of loan', 'draft']
for s in substring:
    dfTransfers['fee'] = dfTransfers['fee'].str.replace(s,'0')

dfTransfers['value'] = np.where(dfTransfers['value'].str.contains('-|\?'), np.nan, dfTransfers['value'])
dfTransfers['fee'] = np.where(dfTransfers['fee'].str.contains('-|\?'), np.nan, dfTransfers['fee'])

substring = ['Loan fee:', '€', 'm', 'Th.', 'â‚¬']
for s in substring:
    dfTransfers['value'] = dfTransfers['value'].str.replace(s,'')
    dfTransfers['fee'] = dfTransfers['fee'].str.replace(s,'')
    dfTransfers['loan_fee'] = dfTransfers['loan_fee'].str.replace(s,'')
    
dfTransfers['value'] = dfTransfers['value'].str.strip()
dfTransfers['fee'] = dfTransfers['fee'].str.strip()
dfTransfers['loan_fee'] = dfTransfers['loan_fee'].str.strip()

dfTransfers['value'] = dfTransfers['value'].astype(float) * dfTransfers['value_mult']
dfTransfers['fee'] = dfTransfers['fee'].astype(float) * dfTransfers['fee_mult']
dfTransfers['loan_fee'] = dfTransfers['loan_fee'].astype(float) * dfTransfers['fee_mult']

dfTransfers = dfTransfers.drop(columns=['value_mult', 'fee_mult'])



dfMeta.to_csv(outputFolder + 'player_metadata.csv', index=False)
dfMV.to_csv(outputFolder + 'player_mv_history.csv', index=False)
dfTransfers.to_csv(outputFolder + 'player_transfer_history.csv', index=False)
