# %% 
import pandas as pd
import numpy as np
from fangraphs_projections import get_projections
import pre_process_script as pp
from league_data import process_league_data
# %% 


# %% 

names = ["steamer", "fangraphsdc", "zipsdc", "razzball", "atc", "thebat", "zips"]
av_names = [] 
bats = pd.DataFrame()
pitch = pd.DataFrame()  
for n in names:
    try:
        # Get projections from Fangraphs
        bats_  = get_projections("all", "bat", n)
        pitch_ = get_projections("all", "pit", n)
        # Concatenate dataframes
        bats = pd.concat([bats, bats_])
        pitch = pd.concat([pitch, pitch_])

        # player_list = player_list.join(ranks, how="inner")
        # player_list.rename(columns={"POINTS":"POINTS_{}".format(n)}, inplace=True)
        # av_names.append("POINTS_{}".format(n))
    except:
        print("{} data unavailable.".format(n))
# %%
bats_mean = bats.groupby("playerid").mean()
pitch_mean = pitch.groupby("playerid").mean()
bats_std = bats.groupby("playerid").std()
pitch_std = pitch.groupby("playerid").std()

bats_mean_rank  = pp.pre_process_bat(bats_mean.reset_index())#.set_index("playerid")#[["POINTS"]]
pitch_mean_rank = pp.pre_process_pitch(pitch_mean.reset_index())#.set_index("playerid")#[["POINTS"]]
pitch_mean_rank.drop(columns=["POS"], inplace=True)
mean_ranks = pitch_mean_rank.add(bats_mean_rank, fill_value=0).sort_values("POINTS", ascending=False)

# %%
def generate_new_projections(means, stds, playerid, type, best_case):
    """_summary_

    Args:
        means (dataframe): Means of the projections
        stds (dataframe): Standard deviations of the projections
        playerid (str): Playerid of the player
        type (str): "bat" or "pit"
        best_case (bool): If True, return best case scenario, otherwise return worst case scenario
    """

    if type == "bat":
        cols_plus = ["G", "AB", "PA", "H", "1B", "2B", "3B", "HR", "R", "RBI", "BB", "IBB", "HBP", "SF", "SH", "SB"]
        cols_minus = ["SO", "CS"]
    elif type == "pit":
        cols_plus = ["GS", "G", "SV", "HLD", "IP", "TBF", "SO"]
        cols_minus = ["R", "ER", "HR", "BB", "HBP", "H"]

    new_projections = means.copy()

    if best_case:
        new_projections.loc[playerid, cols_plus]  += stds.loc[playerid, cols_plus]
        new_projections.loc[playerid, cols_minus] -= stds.loc[playerid, cols_minus]
    else:
        new_projections.loc[playerid, cols_plus]  -= stds.loc[playerid, cols_plus]
        new_projections.loc[playerid, cols_minus] += stds.loc[playerid, cols_minus]

    return new_projections

# %%
id_ = "19755"
best_case = True
new_projections_bat = generate_new_projections(bats_mean, bats_std, id_, "bat", best_case)
new_projections_pit = generate_new_projections(pitch_mean, pitch_std, id_, "pit", best_case)
bats_new_rank  = pp.pre_process_bat(new_projections_bat.reset_index())#.set_index("playerid")#[["POINTS"]]
pitch_new_rank = pp.pre_process_pitch(new_projections_pit.reset_index())#.set_index("playerid")#[["POINTS"]]
pitch_new_rank.drop(columns=["POS"], inplace=True)
new_ranks = pitch_new_rank.add(bats_new_rank, fill_value=0).sort_values("POINTS", ascending=False)
# %%
