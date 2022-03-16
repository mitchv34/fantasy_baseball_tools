import pandas as pd
import numpy as np
from pybaseball import statcast_batter_exitvelo_barrels
# from pybaseball import statcast_batter_expected_stats
import requests
import io

def create_dataframe(retunrs_df=False):
    """
    Create a dataframe from the data
    """

    # get id data
    id_s = pd.read_csv('data/SFBB Player ID Map - PLAYERIDMAP.csv')
    id_s.rename(columns={'PLAYERID': 'player_id'}, inplace=True)
    id_s = id_s[['MLBID', "IDFANGRAPHS"]]
    id_s.dropna(inplace=True)
    id_s.MLBID = id_s.MLBID.astype(int)
    id_s.set_index('MLBID', inplace=True)

    # get exit velocity and barrels data
    # get data for all qualified batters in 2021 with at least 200 at bats
    data_power = statcast_batter_exitvelo_barrels(2021, 200).set_index('player_id')
    data_power = data_power.join(id_s, how = 'inner').sort_values('brl_percent', ascending=False)
    data_power.drop_duplicates( keep='first', inplace=True)
    data_power = data_power[["avg_hit_speed", "brl_pa",	"IDFANGRAPHS"]]
    data_power.rename(columns={'avg_hit_speed': 'exit_velo', 'brl_pa': 'brl', 'IDFANGRAPHS':'playerid'}, inplace=True)
    data_power.set_index('playerid', inplace=True)

    # get expected stats data
    # get data for all qualified batters in 2021 with at least 200 at bats
    year = 2021
    minPA = 200
    
    url = f"https://baseballsavant.mlb.com/leaderboard/custom?year={year}&type=batter&filter=&sort=5&sortDir=desc&min={minPA}&selections=xba,xslg,xwoba,xobp,xiso,&chart=false&x=xba&y=xba&csv=true"
    res = requests.get(url, timeout=None).content
    data_exp = pd.read_csv(io.StringIO(res.decode('utf-8'))).set_index('player_id')
    data_exp = data_exp.join(id_s, how = 'inner').sort_values('xwoba', ascending=False)
    data_exp.drop_duplicates( keep='first', inplace=True)
    data_exp = data_exp[['xba', 'xslg', 'xwoba', 'xobp', 'xiso', "IDFANGRAPHS"]]
    data_exp.rename(columns={'xba': 'xAVG', 'xobp': 'xOBP', 'xslg': 'xSLG', 'xwoba': 'xwOBA', 'xiso':'xISO', 'IDFANGRAPHS':'playerid'}, inplace=True)
    data_exp.set_index('playerid', inplace=True)

    # get percentile ranking data
    # get data for all qualified batters in 2021 with at least 200 at bats
    url = f"https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=batter&year={year}&position=&team=&csv=true"
    res = requests.get(url, timeout=None).content
    data_percent = pd.read_csv(io.StringIO(res.decode('utf-8')))
    # URL returns a null player with player id 999999, which we want to drop
    data_percent = data_percent.loc[data_percent.player_name.notna()].reset_index(drop=True).set_index('player_id')
    data_percent.drop(columns=['oaa', 'player_name', 'year'] , inplace=True)
    data_percent.rename(columns= dict(zip([x for x in data_percent.columns], [x + "_percentile" for x in data_percent.columns])), inplace = True)
    data_percent = data_percent.join(id_s, how = 'inner')
    data_percent.drop_duplicates( keep='first', inplace=True)
    data_percent.rename(columns={'IDFANGRAPHS':'playerid'}, inplace=True)
    data_percent.set_index('playerid', inplace=True)

    data_bats = data_power.join(data_exp, how = 'outer').join(data_percent, how = 'outer')

    # Rename colums to indicate those are batting stats
    data_bats = data_bats.add_suffix('_batting')


    # Add pitchers data
    minPA = 50
    url = f"https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=pitcher&year={year}&position=&team=&min={minPA}&csv=true"
    res = requests.get(url, timeout=None).content
    data_exp = pd.read_csv(io.StringIO(res.decode('utf-8'))).set_index('player_id')
    data_exp = data_exp.join(id_s, how = 'inner').sort_values('est_woba', ascending=False)
    data_exp.drop_duplicates( keep='first', inplace=True)
    data_exp = data_exp[["est_ba", "est_slg", "est_woba", "xera", "IDFANGRAPHS"]]
    data_exp.rename(columns={'est_ba': 'xAVG', 'est_slg': 'xSLG', 'est_woba': 'xwOBA', 'xera': 'xERA', 'IDFANGRAPHS':'playerid'}, inplace=True)
    data_exp.set_index('playerid', inplace=True)

    url = f"https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=pitcher&year={year}&position=&team=&csv=true"
    res = requests.get(url, timeout=None).content
    data_percent = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data_percent = data_percent.loc[data_percent.player_name.notna()].set_index('player_id')
    data_percent.drop(columns=['brl', 'player_name', 'year'] , inplace=True)
    data_percent.rename(columns= dict(zip([x for x in data_percent.columns], [x + "_percentile" for x in data_percent.columns])), inplace = True)
    data_percent = data_percent.join(id_s, how = 'inner')
    data_percent.drop_duplicates( keep='first', inplace=True)
    data_percent.rename(columns={'IDFANGRAPHS':'playerid'}, inplace=True)
    data_percent.set_index('playerid', inplace=True)

    data_pitch = data_power.join(data_exp, how = 'outer').join(data_percent, how = 'outer')

    # Rename colums to indicate those are batting stats
    data_pitch = data_pitch.add_suffix('_pitching')

    # Merge with league player data
    data_league = pd.read_csv('data/proc/league_player_list.csv')
    data_league.set_index('IDFANGRAPHS', inplace=True)

    data = data_league.join(data_bats).join(data_pitch)

    data.to_csv('data/proc/league_player_list_with_statcast.csv')

    if retunrs_df:
        return data
    else:
        return None

# Function to filter data based on percentiles
def filter_percentiles(data, percent, n):
    """
    Filter data by percentile: Return all players that have at least `n` stats in the top `percent` percentile
    """
    columns = [col for col in data.columns if '_percentile' in col]

    subset = data[columns] 
    return data[np.sum(subset > 90, axis=1) > n]
