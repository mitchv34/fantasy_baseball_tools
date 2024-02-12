# %%
import pandas as pd
import json

from bs4 import BeautifulSoup
import requests

# %%

def id_fangraphs(id_list):

    # Dowload the id dictionary
    id_dict = pd.read_csv('/Users/mitchv34/Work/fantasy_baseball_tools/data/SFBB Player ID Map - PLAYERIDMAP.csv')
    


# %% 
def process_league_data(df):
    
    df = df.copy()

    cols = ["ID", "Player", "Team", "Position", "Salary", "ADP"]

    df = df[cols]

    return df


# %%


url = "https://www.fantrax.com/fantasy/league/rvs3p5k8lacksf72/players;seasonOrProjection=SEASON_141_YEAR_TO_DATE;timeframeTypeCode=YEAR_TO_DATE;startDate=2023-03-29;endDate=2023-10-01;pageNumber=1;statusOrTeamFilter=ALL"
response = requests.get(url=url)
soup = BeautifulSoup(response.content, 'html.parser')
# %%

