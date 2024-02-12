# %%
import csv
import json

from bs4 import BeautifulSoup
import requests
# %%

def main():
    url = 'https://www.fangraphs.com/projections?pos=all&stats=bat&type=atc'
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_html = soup.find("script", {"id": "__NEXT_DATA__"})
    table_json = json.loads(table_html.contents[0])
    table = table_json['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']

    # create the csv writer object
    with open('export.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(table[0].keys())
        for player in table:
            # Writing data of CSV file
            csv_writer.writerow(player.values())

# %%
if __name__ == '__main__':
    main()