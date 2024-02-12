# %%
import pandas as pd
import json

from bs4 import BeautifulSoup
import requests
# %%

def get_projections(pos, stats, type_stats):
    url = f'https://www.fangraphs.com/projections?pos={pos}&stats={stats}&type={type_stats}'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_html = soup.find("script", {"id": "__NEXT_DATA__"})
    table_json = json.loads(table_html.contents[0])
    table = table_json['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
    if stats == 'bat':
        cols = ['playerids', 'PlayerName', 'minpos', 'ADP', 'Team', 'ShortName',
                'G', 'AB', 'PA', 'H', '1B', '2B', '3B', 'HR', 'R', 'RBI', 'BB',
                'IBB', 'SO', 'HBP', 'SF', 'SH', 'GDP', 'SB', 'CS']
    elif stats == 'pit':
        cols = ['playerids', 'PlayerName', 'ADP', 'Team', 'ShortName', 
                'GS', 'G', 'SV', 'HLD',  'BS', 'IP', 'TBF', 'H', 'R', 
                'ER', 'HR', 'SO', 'BB', 'HBP']
    table = pd.DataFrame(table)
    table = table[cols]
    table.rename(columns={'playerids': 'player_id'}, inplace=True)
    return table
    # # create the csv writer object
    # with open('export.csv', 'w') as f:
    #     csv_writer = csv.writer(f)
    #     csv_writer.writerow(table[0].keys())
    #     for player in table:
    #         # Writing data of CSV file
    #         csv_writer.writerow(player.values())

# %%
if __name__ == '__main__':
    main()