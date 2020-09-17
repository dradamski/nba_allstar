import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

pd.set_option('mode.chained_assignment', None)
df = pd.read_csv('all-stats-clean.csv', header=0, index_col=0)

# There are many instances of players who took seasons off due to injury/
# health concerns, military service, or to play elsewhere. These instances 
# screwed up the data scraping process so they require additional cleaning.
# This is done by systematically going through and checking Basketball
# Reference and adjusting their stats accordingly by hand. I wanted to do it
# programmatically, but the juice wasn't worth the squeeze.

df = df.replace('None', np.nan)
df.columns = df.columns.str.lower()

df.rename(columns={'fg%':'fgp','3p':'threep', '3pa':'threepa',
                  '3p%':'threepp', '2p':'twop', '2pa':'twopa',
                  '2p%':'twopp', 'efg%':'efgp', 'ft%':'ftp'}, inplace=True)

# Edit positions to only include position player play
def slice(string):
    if type(string) == str:
        a = string.split('-')
        return a[0]        
df.pos = df.pos.apply(slice)

    

# Convert columns to number formats
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='ignore')

# Add All Star category
allstar= {'allstar':[]}
for i, row in df.iterrows():
    try:
        len(row['season'])
        allstar['allstar'].append(0)
    except:
        allstar['allstar'].append(1)
df['allstar'] = allstar['allstar']



# I will also need to deal with players who were traded mid season. I am going
# to solely look at their totals over the course of the entire season
df = df.loc[df.age.shift(1) != df.age]
df = df.reset_index(drop=True)


# Convert heights of players to inches
def fix_height(ht):
    ft, inch = ht.split('-')
    new_ht = 12*int(ft) + int(inch)
    return(new_ht)

height = np.empty(len(df))
for i, h in enumerate(df.height):
    if '-' in h:
        height[i] = fix_height(h)
    else:
        height[i] = h
df.height = pd.to_numeric(height)

# Looking through describe
# pos has 6 unique values? TRUE PG, SG, SF, PF, C, nan
# g max is 88 ACCURATE
# fg and fga potentially have outliers
# fgp max is 1.000 which does not make sense to include
# threepa max doesnt make sense JUST JAMES HARDEN
# threepp should be checked ADD SOMETHING THAT SAYS PLAYER HAS TO AVG  >.1
# twopa and fga should be equal IF TWOPA == nan, TWOPA=FGA
twopa = np.empty(len(df))
twopp = np.empty(len(df))
twop = np.empty(len(df))

for i, t in enumerate(df.twop):
    if np.isnan(t):
        twop[i] = df.fg[i]
        twopa[i] = df.fga[i]
        twopp[i] = df.fgp[i]
    else:
        twop[i] = df.twop[i]
        twopa[i] = df.twopa[i]
        twopp[i] = df.twopp[i]
df.twopa = twopa
df.twopp = twopp
df.twop = twop

# twopp max is above 1
# ftp is 736 FIXED
# orb is 7.2 TRUE
# drb is 13.7 TRUE
# blk max is 5 TRUE

# Need to fix threepp for players who did not take 3's during 3pt era
# see Dikembe Mutumbo
threepp = np.empty(len(df))
for i, row in df.iterrows():
    if np.isnan(row.threepp) and not (np.isnan(row.threepa) and np.isnan(row.threep)) :
        threepp[i] = 0
    else:
        threepp[i] = row.threepp
        
df.threepp = threepp        


# Add years in the league
unique = df.player.unique()
years_in_league = []
for player in unique:
    playerdf = df[df.player == player]
    years_in_league += list(range(1, len(playerdf)+1))
years_in_league = pd.DataFrame({'years_in_league':years_in_league})
df['years_in_league'] = years_in_league


# Impute values using position based means

pgdf = df[df.pos == 'PG']
sgdf = df[df.pos == 'SG']
sfdf = df[df.pos == 'SF']
pfdf = df[df.pos == 'PF']
cdf = df[df.pos == 'C']

positions = [pgdf, sgdf, sfdf, pfdf, cdf]

def position_imputation(df):
    for col in df:
        if np.dtype(df[col]) != object:
            col_ser = df[col]
            indexes = df.index
            col_arr = np.array(col_ser).reshape(-1,1)
            
            imp = SimpleImputer(missing_values=np.nan, strategy='mean',
                               fill_value=True)
            col_arr = imp.fit_transform(col_arr)
            col_df = pd.DataFrame(col_arr, index=indexes)
            df[col] = col_df
    return df

for position in positions:
    position = position_imputation(position)

df = pd.concat(positions).sort_index()

# Remove all rows without missing values
df = df.drop(columns='season')


# Create column that states whether a player will be an allstar the following
# year
allstar_next = pd.DataFrame()
for player in df.player.unique():
    playdf = df[df.player == player]
    playallstar_next = playdf.allstar[1:]
    playallstar_next = pd.concat([playallstar_next, pd.Series([0])])
    playallstar_next.index = playdf.index
    allstar_next = pd.concat([allstar_next, playallstar_next])
df['allstar_next'] = allstar_next

df = df.dropna()
df = df.reset_index(drop=True)