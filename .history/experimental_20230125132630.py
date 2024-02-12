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
for n in names:
    try:
        # Get projections from Fangraphs
        bats  = get_projections("all", "bat", n)
        pitch = get_projections("all", "pit", n)
        bats  = pp.pre_process_bat(bats).set_index("playerid")#[["POINTS"]]
        pitch = pp.pre_process_pitch(pitch).set_index("playerid")#[["POINTS"]]
        # ranks = pitch.add(bats, fill_value=0).sort_values("POINTS")
        # player_list = player_list.join(ranks, how="inner")
        # player_list.rename(columns={"POINTS":"POINTS_{}".format(n)}, inplace=True)
        # av_names.append("POINTS_{}".format(n))
        break
    except:
        print("{} data unavailable.".format(n))
# %%
