from bs4 import BeautifulSoup
import pandas as pd
import urllib.request

# Access Basketball Reference to get league leaders in win shares for each season
#specify the url
site = "https://www.basketball-reference.com/leaders/hof_prob.html"
#Query the website and return the html to the variable 'page'
page = urllib.request.urlopen(site)
#Parse the html in the 'page' variable and store it in Beautiful Soup format
soup = BeautifulSoup(page, 'lxml')

# Save two Hall of Fame Probability leader tables (all time and active)
alltime_table, active_table = soup.find_all('table')

#create list of tuples containgin player name and player page link 
alltime_list = []
active_list = []
for line in alltime_table('td'):
    try:
        alltime_list.append((str(line.a.string), str(line.a.get('href'))))
    except:
        print('could not do it for', line)
        
for line in active_table('td'):
    try:
        active_list.append((str(line.a.string), str(line.a.get('href'))))
    except:
        print('could not do it for', line)

# Create list of players on active_list but not alltime_list
# and add to alltime_list
active_list = list(set(active_list).difference(set(alltime_list)))
alltime_list += active_list


# This for loop gets the season by season stats for each player in the 
# alltime_list. First it turns the player page html into a Beautiful Soup
# object to make the stats table. I also pull the player's height from
# the top of the page, and convert it from a string 'x-xx' to inches.
all_seasons = [] 
for player in alltime_list:
    reference_site = 'https://www.basketball-reference.com' + player[1]
    page = urllib.request.urlopen(reference_site)
    soup = BeautifulSoup(page, 'lxml')
    per_game_table = soup.table
    
    height_str = str(soup.find_all('div', {'id':'info'})[0].find_all('span', {'itemprop':'height'})[0].string)
    height = height_str.split('-')
    height = int(height[0])*12 + int(height[1])
    
    # This section gets stats values for a single season and 
    # makes a single list
    values = []
    length = 0
    for row in (per_game_table('tr')):
        for num, column in enumerate(row):
            # Players from different decades have different
            # available stats, but PTS is always the last column
            if column.string == 'PTS':
                length = int((num+1) / 2)
            if column != '\n':
                values.append(str(column.string))
    categories = values[:length]
    # Ignores category names
    values = values[length:]

    # Create list of individual season stats lists
    player_career = [['Player', 'href', 'Height'] + categories]
    season = [player[0], player[1], height]
    for value in values:
        if value.startswith('Did'):
            # Find players who took time off mid-career
            print(player[0], value)
        season.append(str(value))
        #added and (season[3] != None)
        if (len(season) == length+3) and (season[4] != 'None'):
            player_career.append(season)
            season = [player[0], player[1], height]
        # Player must have played at least 12 seasons
    #if (len(player_career) > 12):# and (len(player_career[0]) == 33):
    all_seasons.append(player_career)
    print(str((len(player_career)-1)), ' seasons of ', player[0], 'added')



# Create pandas DataFrame of all data
category_list= ['Player', 'href', 'Height', 'Season', 'Age', 'Tm', 'Lg', 
                'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', 
                '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'
                ]

            
            
# CREATE LIST OF DATAFRAMES AND MERGE AT END
df_list = []
season_df_list = []
master_df = pd.DataFrame(columns=category_list)
for career in all_seasons:
    labels=career[0]
    for season in career[1:]:
        season_df = pd.DataFrame(data=season, index=labels)
        season_df_list.append(season_df.transpose())
career_df = pd.concat(season_df_list, ignore_index=True)
    

career_df.to_csv('all-stats-messy.csv', columns = category_list)
