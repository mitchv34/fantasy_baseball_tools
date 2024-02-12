# Load libraries
import pandas as pd
import numpy as np

# Function to get ranks for each player in each stat
def get_ranks(df, stat, ascending=True):
    rank = 10*(df[stat] - np.min(df[stat]) ) / (np.max(df[stat]) - np.min(df[stat]) )
    if ascending:
        return rank
    else:
        return 10-rank

# Function to infer if a pitcher is a starter or not
def get_ptch_POS(df):
    POS = []
    for i in df['GS']:
        if i > 0:
            POS.append('SP')
        else:
            POS.append('RP')
    return POS

# A simple regression model to predict the number of OS games a starter will make
def get_QS(df):
    QS = np.round( len(df)*[-2.095412] + 0.173737*df['IP'] +  0.003827*df['K'] -0.074804*df['BB'] -0.122394*df['HR'] -0.055386*(df['H']-df['HR']) )
    QS[df['POS']=='RP'] = [0]*len(QS)
    return QS

# Function to add Fangraphs ID to the league data
def add_fg_id():
    # Load data

    # Id data
    id_map = pd.read_csv('data/SFBB Player ID Map - PLAYERIDMAP.csv')

    # League data
    legue_players = pd.read_csv("data/league/Fantrax-Players-Believers in BABIP (BIB).csv")
    legue_players = legue_players[["ID", "Player", "Position", "Status", "Age", "ADP"]]

    # Subset of interest
    id_map_subset = id_map[["IDFANGRAPHS",  "FANTRAXID"]]
    id_map_subset.columns = ["IDFANGRAPHS", "ID"]

    # Merge to get Fangraphs ID and drop players with no Fangraphs ID
    legue_players = legue_players.merge(id_map_subset, on="ID", how="inner")

    # Remove duplicate players (Shoei Ohtani)
    legue_players.drop_duplicates(inplace=True)

    # Save data
    legue_players.to_csv("./data/proc/league_player_list.csv", index=False)

    return None

# Pre-process batter data
def pre_process_bat(df, min_pa = 250):
    # Read in data
    df.set_index('playerid', inplace = True, drop=False)
    # Drop players with less than min_pa PA
    df = df[df['PA']>min_pa]
    # Rename columns
    dic_cols = {'SO':'K'}
    df.rename(columns=dic_cols, inplace = True)
    # Create new relevant stats
    df['NSB'] = df['SB'] - df['CS']
    df['K%'] = df['K'] / df['AB']
    df['BB%'] = df['BB'] / df['PA']

    if "HBP" not in df.columns:
        df["HBP"] = [0]*len(df)

    if "SF" not in df.columns:
        df["SF"] = [0]*len(df)

    if "SH" not in df.columns:
        df["SH"] = [0]*len(df)

    if "TB" not in df.columns:
        df["TB"] = df['H'] + df['2B'] +2*df['3B'] + 3*df['HR']
    
    # This variable will control for the standard roster size
    r_size = 11
    # Creat the values of a "mean" player
    mean_PA = np.mean(df['PA'])
    mean_AB = np.mean(df['AB'])
    mean_H = np.mean(df['H'])
    mean_2B = np.mean(df['2B'])
    mean_3B = np.mean(df['3B'])
    mean_HR = np.mean(df['HR'])
    mean_BB = np.mean(df['BB'])
    mean_HBP = np.mean(df['HBP'])
    # Create weighted average of stats
    df["wAVG"] = ((df['H'] + r_size*mean_H) / (df['AB'] + r_size*mean_AB) - mean_H/mean_AB)*100
    df["wOBP"] =  ((df['H'] + df['BB'] + df['HBP'] + r_size*(mean_H + mean_BB + mean_HBP) )/ (df['PA'] + r_size*mean_PA) \
                    - (mean_H + mean_BB + mean_HBP) / mean_PA)*100
    df["wSLG"] = ((df['H'] + df['2B'] +2*df['3B'] + 3*df['HR'] + r_size*(mean_H + mean_2B + 2*mean_3B + 3*mean_HR)\
                    )/ (df['AB'] + r_size*mean_AB)- (mean_H + mean_2B + 2*mean_3B + 3*mean_HR) /mean_AB)
    df["wOPS"] = df["wSLG"] + df["wOBP"]

    # Stats we want to rank
    Ranks_of_interest = ['R', 'RBI', 'H', 'HR', 'K%', 'BB%', 'NSB', 'wAVG', 'wOBP', 'wSLG', 'wOPS']
    # How we want to rank them
    Ascending = ['True', 'True', 'True', 'True', 'False', 'True', 'True', 'True', 'True', 'True']
    # Create ranks
    for stat in  Ranks_of_interest:
        df['r'+stat] = get_ranks(df, stat, ascending=(stat != 'K%' ))
    # Sum up ranks to get overall rank
    df['POINTS'] = df[list(map('r'.__add__,Ranks_of_interest))].sum(1)

    return None

# Pre-process pitcher data
def pre_process_pitch(df):

    # Read in data
    df.set_index('playerid', inplace = True, drop=False)
    dic_cols = {"SO":"K"}
    df.rename(columns=dic_cols, inplace = True)

    # Initialize variable Holds
    df["HLD"] = [0] * len(df)

    # Fill in Holds and Saves from projection systems that have them
    # Data not available
    # if name in ["steamer", "depthcharts"]:
    #     holds = pd.read_csv(root + "/data/razzball_pitch.csv").set_index("Name")['SV']
    #     for p in df.index:
    #         if p in holds.index:
    #             df.loc[p, "HLD"] = holds.loc[p]

    # if name == "ZiPS":
    #     df["SV"] = [0] * len(df)
    #     holds = pd.read_csv(root + "/data/razzball_pitch.csv").set_index("Name")['SV']
    #     for p in df.index:
    #         if p in holds.index:
    #             df.loc[p, "SV"] = holds.loc[p]

    # if name == "thebat":
    #     df["SV"] = [0] * len(df)
    #     holds = pd.read_csv(root + "/data/razzball_pitch.csv").set_index("Name")['SV']
    #     for p in df.index:
    #         if p in holds.index:
    #             df.loc[p, "SV"] = holds.loc[p]


    # if name == "ATC":
    #     rz_p = pd.read_csv(root + "/data/razzball_pitch.csv").set_index("Name")
    #     rz_p.rename(columns=dic_cols, index=dic_index, inplace = True)
    #     id_ = set(df.index).intersection(rz_p.index)
    #     rz_p= rz_p.loc[id_]
    #     df = df.loc[id_]
    #     df["HLD"] = rz_p["HLD"]
    

    # Infer if a pitcher is a starter or not
    df["POS"] = get_ptch_POS(df)
    # Predict QS for starters
    df["QS"] = get_QS(df)
    
    # Roster size
    SP_size, RP_size= 5, 6
    
    # Segment the data by position
    SP = df[df['POS']=='SP']
    RP = df[df['POS']=='RP']
    
    # Create "mean" starter
    mean_SP_IP = np.mean(SP['IP'])
    mean_SP_ER = np.mean(SP['ER'])
    mean_SP_H = np.mean(SP['H'])
    mean_SP_BB = np.mean(SP['BB'])
    mean_SP_K = np.mean(SP['K'])
    # Create "mean" relief pitcher
    mean_RP_IP = np.mean(RP['IP'])
    mean_RP_ER = np.mean(RP['ER'])
    mean_RP_H = np.mean(RP['H'])
    mean_RP_BB = np.mean(RP['BB'])
    mean_RP_K = np.mean(RP['K'])
    
    # Create weighted average of stats
    df['wERA'] = 9*((df['ER'] + SP_size*mean_SP_ER + RP_size*mean_RP_ER)/(df['IP'] + SP_size*mean_SP_IP + RP_size*mean_RP_IP)\
                -((mean_SP_ER+mean_RP_ER)/2 + SP_size*mean_SP_ER + RP_size*mean_RP_ER)/((mean_RP_IP+mean_SP_IP)/2 + SP_size*mean_SP_IP + RP_size*mean_RP_IP))

    df['wWHIP'] = ((df['H']+df['BB']) + (SP_size*mean_SP_H + SP_size*mean_SP_BB) + (RP_size*mean_RP_H + RP_size*mean_RP_BB))/(df['IP'] + SP_size*mean_SP_IP + RP_size*mean_RP_IP)\
                -((mean_SP_H+mean_SP_BB+mean_RP_H+mean_RP_BB)/2 + (SP_size*mean_SP_H + SP_size*mean_SP_BB) + (RP_size*mean_RP_H + RP_size*mean_RP_BB))/((mean_RP_IP+mean_SP_IP)/2 + SP_size*mean_SP_IP + RP_size*mean_RP_IP)
    df['wK/9'] = 9*((df['K'] + SP_size*mean_SP_K + RP_size*mean_RP_K)/(df['IP'] + SP_size*mean_SP_IP + RP_size*mean_RP_IP)\
                -((mean_SP_K+mean_RP_K)/2 + SP_size*mean_SP_K + RP_size*mean_RP_K)/((mean_RP_IP+mean_SP_IP)/2 + SP_size*mean_SP_IP + RP_size*mean_RP_IP))
    df['wBB/9'] = 9*((df['BB'] + SP_size*mean_SP_BB + RP_size*mean_RP_BB)/(df['IP'] + SP_size*mean_SP_IP + RP_size*mean_RP_IP)\
                -((mean_SP_BB+mean_RP_BB)/2 + SP_size*mean_SP_BB + RP_size*mean_RP_BB)/((mean_RP_IP+mean_SP_IP)/2 + SP_size*mean_SP_IP + RP_size*mean_RP_IP))
    df['wH/9'] = 9*((df['H'] + SP_size*mean_SP_H + RP_size*mean_RP_H)/(df['IP'] + SP_size*mean_SP_IP + RP_size*mean_RP_IP)\
                -((mean_SP_H+mean_RP_H)/2 + SP_size*mean_SP_H + RP_size*mean_RP_H)/((mean_RP_IP+mean_SP_IP)/2 + SP_size*mean_SP_IP + RP_size*mean_RP_IP))
    df['wK/BB'] = 9*((df['K'] + SP_size*mean_SP_K + RP_size*mean_RP_K)/(df['BB'] + SP_size*mean_SP_BB + RP_size*mean_RP_BB)\
                -((mean_SP_K+mean_RP_K)/2 + SP_size*mean_SP_K + RP_size*mean_RP_K)/((mean_RP_BB+mean_SP_BB)/2 + SP_size*mean_SP_BB + RP_size*mean_RP_BB))
    RAPP = []
    for i,j in zip(df['POS'],df['G']):
        if i == 'RP':
            RAPP.append(j)
        else:
            RAPP.append(0)
    df["RAPP"] = RAPP

    # Stats we want to rank
    Ranks_of_interest = ['IP', 'wERA', 'wWHIP', 'wK/9', 'wBB/9', 'wH/9', 'wK/BB', 'SV', 'HLD', 'QS', 'RAPP']
    # How to rank them
    Asscending = [True, False, False, True, False, False, True, True, True, True, True]
    for stat,mask in  zip(Ranks_of_interest, Asscending):
        df['r'+stat] = get_ranks(df, stat, ascending=mask)
    # Sum up the ranks for each player to get a total rank
    df['POINTS'] = df[list(map('r'.__add__,Ranks_of_interest))].sum(1)

    return None
