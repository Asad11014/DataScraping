from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

all_teams = []  # List to store all teams' data

html = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats').text
soup = BeautifulSoup(html, 'lxml')
table = soup.find_all('table', class_='stats_table')[0]

links = table.find_all('a')
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]

team_urls = [f"https://fbref.com{l}" for l in links]

for team_url in team_urls:
    team_name = team_url.split("/")[-1].replace("-Stats", "")
    data = requests.get(team_url).text
    soup = BeautifulSoup(data, 'lxml')
    stats = soup.find_all('table', class_='stats_table')[0]

    if stats and stats.columns:
        stats.columns = stats.columns.droplevel()

    # Convert the HTML table to a DataFrame
    team_data = pd.read_html(str(stats))[0]

    # Filter out specific columns
    columns_to_drop = ['Unnamed: 4_level_0', 'Unnamed: 33_level_0']
    team_data = team_data.drop(columns=columns_to_drop, errors='ignore')

    # Add team name as a column
    team_data['Team'] = team_name

    # Append team data to the list
    all_teams.append(team_data)

    time.sleep(5)  # Delay to avoid overloading the server

# Concatenate all teams' data into a single DataFrame
if all_teams:
    stat_df = pd.concat(all_teams)

    # Save the concatenated DataFrame to a CSV file
    stat_df.to_csv("stats.csv", index=False)
    print("Data has been saved to stats.csv")
else:
    print("No team data found.")
