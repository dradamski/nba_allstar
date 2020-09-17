from bs4 import BeautifulSoup, Comment
from itertools import chain
import numpy as np
import os
import pandas as pd
import urllib.request



def go_to_player_page(player):

    """
    Takes player tuple and returns BeautifulSoup object of page
    
    Parameters
    ----------
    
    player : tuple
       
       player tuple comes in format (
    """


    reference_site = 'https://www.basketball-reference.com' + player[1]
    page = urllib.request.urlopen(reference_site)
    soup = BeautifulSoup(page, 'lxml')

    return soup




def get_team_links(year):
    """
    When given a year, this function pulls
    goes to that season's basketball-reference
    page and pulls links to every team's year
    specific page.
       
    Parameters
    ----------

    year : int
       season from which you would like to pull team links from.
       2020 == 2019-2020 season
    
    Returns
    -------: [https://www.basketball-reference.com/teams/DAL/2020.html,
             https://www.basketball-reference.com/teams/MIL/2020.html,
             https://www.basketball-reference.com/teams/HOU/2020.html,
             ...
             ]
    """
    reference_site = 'https://www.basketball-reference.com/leagues/NBA_{}.html'.format(str(year))
    page = urllib.request.urlopen(reference_site)
    soup = BeautifulSoup(page, 'lxml')
    
    table = soup.find(id='all_team-stats-per_game')

    for comment in table.find_all(string=lambda text:isinstance(text,Comment)):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        team_table = comment_soup.find("table")

    return [tr.a['href'] for tr in team_table.find_all('tr') if tr.a != None]



def get_players_from_team_link(team_link):
    """When given list of team page href, this
       function pulls all the players that were
       on those team rosters.
       
       Ex:
       input: /teams/MIL/2020.html
       output: {('Brook Lopez', '/players/l/lopezbr01.html'),
                ('Cameron Reynolds', '/players/r/reynoca01.html'),
                ('D.J. Wilson', '/players/w/wilsodj01.html'),
                ('Donte DiVincenzo', '/players/d/divindo01.html'),
                ...
                }
    """
    
    link = 'https://www.basketball-reference.com{}'.format(team_link)
    page = urllib.request.urlopen(link)
    soup = BeautifulSoup(page, 'lxml')
    
    print(team_link)
    player_list = set()
        
    player_set = {(i.text, i['href']) for i in soup.find_all('table')[0].find_all('a') if 'players' in i['href']}
    return player_set


def get_stats(player_set,
              all_season_df=pd.DataFrame(),
              x=0
             ):
    """
    Takes a set of players and pulls their per_game stats
    
    Parameters
    ----------
    
    player_set : set of tuples
    
    
    
    all_season_df: pandas dataframe
    
    
    
    x : int
    
    
    
    Returns
    -------
    
    """
    
    for player in player_set:
        soup = go_to_player_page(player)
        per_game_table = soup.table
       
        print('Starting with {}'.format(player_df.Player.unique()))

        # Excludes rookies from the table
        if per_game_table != None:
            raw_height = str(soup.find_all('div', {'id':'info'})[0].find_all('span', {'itemprop':'height'})[0].string)
            height_tup = raw_height.split('-')
            height = int(height_tup[0])*12 + int(height_tup[1])
            player_df = pd.read_html(reference_site)[0]
            player_df['Height'] = height
            player_df['href'] = player[1]
            player_df['Player'] = player[0]

            # removes career totals
            player_df = player_df[player_df.Season != 'Career']
            # removes seasons where players did not play
            player_df = player_df[player_df.Tm != player_df.Lg]
            # remove totals for each team player played on
            player_df = player_df[player_df.Age.notna()]
            # trim season stat to be the starting year
            player_df['Season'] = player_df.Season.str[:4]
            
            all_season_df = all_season_df.append(player_df)
            x += 1
            
            if x % 10 == 0:
                print(x, player_df.Player.unique())

    return all_season_df




def get_df_starts(player_soup):

    """
    Takes BS4 soup object and identifies locations of each additional
       player stat tables
    """
    if player_soup.table != None:
        
        all_list = []
        
        for comment in player_soup.find_all(string=lambda text:isinstance(text,Comment)):
            data=BeautifulSoup(comment, "lxml")
            for items in data.select("table.row_summable tr"):
                tds = [item.get_text(strip=True) for item in items.select("th,td")]
                all_list.append(tds)
        # get index of table headers
        df_starts = []
        for i, row in enumerate(all_list):
            if row[0] == 'Season':
                df_starts.append(i)
    return all_list, df_starts



def pick_stats(stat_list, df_starts):
    """
    List of potential stats : 'totals', 'per36', 'per100', 'advanced',
                              'adjusted_shooting', 'shooting', 'play_by_play',
                              'game_highs', 'playoff_per_game', 'playoff_totals',
                              'playoff_per36', 'playoff_per100',
                              'playoff_advanced', 'playoff_shooting',
                              'playoff_play_by_play','playoff_game_highs',
                              'all_star_games'
    """
    
    tables = ['totals', 'per36', 'per100', 'advanced',
              'adjusted_shooting', 'shooting', 'play_by_play',
              'game_highs', 'playoff_per_game', 'playoff_totals',
              'playoff_per36', 'playoff_per100', 'playoff_advanced',
              'playoff_shooting', 'playoff_play_by_play',
              'playoff_game_highs', 'all_star_games']
    
    
    used_tables = tables[:len(df_starts)]
    
    stat_indexes = [used_tables.index(stat) for stat in stat_list]
    
    return stat_indexes




def get_stats_from_page(all_list, stat_index, player):
    # create table of advanced stats
    table = [row for row in all_list[df_starts[stat_index]:df_starts[stat_index+1]]]

    # convert each table to a DataFrame and add to list of dataframes
    cols = ['Player', 'href'] + table[0]
    player_df = pd.DataFrame(table[1:], columns=table[0])
    player_df['Player'] = player[0]
    player_df['href'] = player[1]

    player_df.replace('', np.nan, inplace=True)
    # remove totals for each team player played on
    player_df = player_df[player_df.Age.notna()]
    # trim season stat to be the starting year
    player_df['Season'] = player_df.Season.str[:4]

    return player_df
