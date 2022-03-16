import warnings
from IPython.display import clear_output
import pandas as pd
import numpy as np
import pathlib

root = str(pathlib.Path().absolute()).replace("\\", "/")

def get_ranks(df, stat, ascending=True):
    rank = 10*(df[stat] - np.min(df[stat]) ) / (np.max(df[stat]) - np.min(df[stat]) )
    if ascending:
        return rank
    else:
        return 10-rank
def get_ptch_POS(df):
    POS = []
    for i in df['GS']:
        if i > 0:
            POS.append('SP')
        else:
            POS.append('RP')
    return POS

def get_QS(df):
    QS = np.round( len(df)*[-2.095412] + 0.173737*df['IP'] +  0.003827*df['K'] -0.074804*df['BB'] -0.122394*df['HR'] -0.055386*(df['H']-df['HR']) )
    QS[df['POS']=='RP'] = [0]*len(QS)
    return QS

def pre_process_bat(name, min_pa = 250):
    df = pd.read_csv(root + "/data/projections/{}_bats.csv".format(name))
    df.set_index('Name', inplace = True, drop=False)
    df = df[df['PA']>min_pa]
    dic_cols = {'SO':'K'}
    dic_index = {"Giovanny Urshela":"Gio Urshela", "Will Smith" : "Will Smith (Batter)",
                 "Peter Alonso":"Pete Alonso", "Shohei Ohtani": "Shohei Ohtani (Batter)"}
    df.rename(columns=dic_cols, index=dic_index, inplace = True)
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
    
    r_size = 11
    mean_PA = np.mean(df['PA'])
    mean_AB = np.mean(df['AB'])
    mean_H = np.mean(df['H'])
    mean_2B = np.mean(df['2B'])
    mean_3B = np.mean(df['3B'])
    mean_HR = np.mean(df['HR'])
    mean_BB = np.mean(df['BB'])
    mean_HBP = np.mean(df['HBP'])
    df["wAVG"] = ((df['H'] + r_size*mean_H) / (df['AB'] + r_size*mean_AB) - mean_H/mean_AB)*100
    df["wOBP"] =  ((df['H'] + df['BB'] + df['HBP'] + r_size*(mean_H + mean_BB + mean_HBP) )/ (df['PA'] + r_size*mean_PA) \
                    - (mean_H + mean_BB + mean_HBP) / mean_PA)*100
    df["wSLG"] = ((df['H'] + df['2B'] +2*df['3B'] + 3*df['HR'] + r_size*(mean_H + mean_2B + 2*mean_3B + 3*mean_HR)\
                    )/ (df['AB'] + r_size*mean_AB)- (mean_H + mean_2B + 2*mean_3B + 3*mean_HR) /mean_AB)
    df["wOPS"] = df["wSLG"] + df["wOBP"]

    # fOR DANIASTY
    A = df['BB'] + df['H'] - df['CS'] + df['HBP']
    B = df['TB'] + 0.26*(df['BB'] + df['HBP'])
    C = 0.52*(df['SF'] + df['SH'] +df['SB'])
    D = df['BB'] + df['AB'] + df['SF'] + df['SH'] + df['HBP']



    df["RC"] = (A*B + C)/D
    # Ranks_of_interest = ['HR', 'NSB', 'wOBP', 'wSLG', 'RC']
    # Ascending = [True, True, True, True, True]
    Ranks_of_interest = ['R', 'RBI', 'H', 'HR', 'K%', 'BB%', 'NSB', 'wAVG', 'wOBP', 'wSLG', 'wOPS']
    Ascending = ['True', 'True', 'True', 'True', 'False', 'True', 'True', 'True', 'True', 'True']
    for stat in  Ranks_of_interest:
        df['r'+stat] = get_ranks(df, stat, ascending=(stat != 'K%' ))
    df['POINTS'] = df[list(map('r'.__add__,Ranks_of_interest))].sum(1)
    return df

def pre_process_pitch(name):
    df = pd.read_csv(root + "/data/projections/{}_pitch.csv".format(name))
    df.set_index('Name', inplace = True, drop=False)
    dic_cols = {"SO":"K"}
    dic_index = {'Joshua James':"Josh James", "Shohei Ohtani": "Shohei Ohtani (Pitcher)", 
                 "Will Smith" : "Will Smith (Pitcher)",}
    df.rename(columns=dic_cols, index=dic_index, inplace = True)

    conflict = ['Luis Garcia', 'Javy Guerra']
    for i in conflict:
        df.drop(index=i, inplace=True)


    df["HLD"] = [0] * len(df)

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
    
    df["POS"] = get_ptch_POS(df)
    
    df["QS"] = get_QS(df)
    
    SP_size, RP_size= 5, 6
    
    SP = df[df['POS']=='SP']
    RP = df[df['POS']=='RP']
    
    mean_SP_IP = np.mean(SP['IP'])
    mean_SP_ER = np.mean(SP['ER'])
    mean_SP_H = np.mean(SP['H'])
    mean_SP_BB = np.mean(SP['BB'])
    mean_SP_K = np.mean(SP['K'])

    mean_RP_IP = np.mean(RP['IP'])
    mean_RP_ER = np.mean(RP['ER'])
    mean_RP_H = np.mean(RP['H'])
    mean_RP_BB = np.mean(RP['BB'])
    mean_RP_K = np.mean(RP['K'])
    
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
    
    # For dynasty
    # df["SVH2"] = df["SV"] + 0.5*df["HLD"]
    # Ranks_of_interest = ['wERA', 'wWHIP', 'wK/9','SVH2', 'QS']
    # Asscending =       [False, False, True, True, True]
    # 

    Ranks_of_interest = ['IP', 'wERA', 'wWHIP', 'wK/9', 'wBB/9', 'wH/9', 'wK/BB', 'SV', 'HLD', 'QS', 'RAPP']
    Asscending = [True, False, False, True, False, False, True, True, True, True, True]
    for stat,mask in  zip(Ranks_of_interest, Asscending):
        df['r'+stat] = get_ranks(df, stat, ascending=mask)
    df['POINTS'] = df[list(map('r'.__add__,Ranks_of_interest))].sum(1)
    df.loc["Shohei Ohtani (Pitcher)", "HLD"] = 0
    return df

def get_ranks_bats():
    
    names = ["steamer", "depthcharts", "razzball", "ATC", "thebat", "ZiPS"]

    col_names = []
    for n in names:
        try:
            if 'composite' in locals():
                composite = pd.merge(composite, pre_process_bat(n)['POINTS'].to_frame(), how='inner', left_index=True, right_index=True)
            else:
                composite = pre_process_bat(n)["POINTS"].to_frame()            
            col_names.append(n)
        except:
            print("missing stats from {}".format(n))            

    composite['MEAN'] = composite.mean(axis=1)
    composite['VAR'] = composite.loc[:, composite.columns!="MEAN"].var(axis=1)
    composite.sort_values('MEAN', axis=0, ascending=False, inplace=True)

    composite.columns = ["Points_{}".format(i) for i in col_names] + ["MEAN", "VAR"]

    return composite

def get_ranks_pitch():
    
    names = ["steamer", "depthcharts", "razzball", "ATC", "thebat", "ZiPS"]
    
    col_names = []
    for n in names:
        try:
            if 'composite' in locals():
                composite = pd.merge(composite, pre_process_pitch(n)['POINTS'].to_frame(), how='inner', left_index=True, right_index=True)
            else:
                composite = pre_process_bat(n)["POINTS"].to_frame()            
            col_names.append(n)
        except:
            print("missing stats from {}".format(n))            

    composite['MEAN'] = composite.mean(axis=1)
    composite['VAR'] = composite.loc[:, composite.columns!="MEAN"].var(axis=1)
    composite.sort_values('MEAN', axis=0, ascending=False, inplace=True)

    composite.columns = ["Points_{}".format(i) for i in col_names] + ["MEAN", "VAR"]

    return composite


def get_ranks_totales():
    ADP = pd.read_csv(root + '/data/league/Fantrax-Players-Believers in BABIP (BIB).csv')
    ADP = ADP[["Player", "Position", "Status","Age","ADP"]]
    ADP.rename(columns = {'Player':'Name', 'ADP_Rank':'ADP'}, inplace=True)
    ADP['Name'] = [" ".join(n.split(", ")[::-1]) for n in ADP['Name']]
    ADP.set_index('Name', inplace=True)

    bat = get_ranks_bats()
    bat.rename(columns = {'POSITIONS':'POS'}, inplace = True)
    #bat.loc["Shohei Ohtani", "POS"] = "UT"
    pitch = get_ranks_pitch()
    # unified = (bat.loc["Shohei Ohtani"] + pitch.loc["Shohei Ohtani"]).to_frame().transpose()
    
    bat = bat.merge(ADP,  how='inner', left_index=True, right_index=True)
    pitch = pitch.merge(ADP,  how='inner', left_index=True, right_index=True)
    #unified = unified.merge(ADP[['ADP_Rank', 'Min Pick', 'Max Pick']],  how='inner', left_index=True, right_index=True)

    bat.rename(index={"Shohei Ohtani":"Shohei Ohtani (Bat)"}, inplace=True)
    pitch.rename(index={"Shohei Ohtani":"Shohei Ohtani (Pitch)"}, inplace=True)

    df = pd.concat([bat, pitch])#, unified])

    df.sort_values('MEAN', axis=0, ascending=False, inplace=True)
    df['Rank'] = list(range(1,len(df)+1))
    # df['ADP vs Rank'] = df['ADP_Rank'] - df['Rank']
    
    return df.sort_values("Rank")


def draft_companion(teams=None):

    Index_of_interest_bats = ['PA', 'AB', 'H', '2B', '3B', 'HR', 'R', 'RBI', 'BB', 'K', 'HBP', 'SB', 'CS']
    Index_of_interest_pitcher = ['POS', 'IP', 'H', 'HR', 'ER', 'BB', 'K', 'SV', 'HLD', 'QS', 'RAPP']
    names = ["steamer", "depthcharts", "razzball", "ATC", "thebat", "ZiPS"]
    
    for n in names:
        try:
            if n == "steamer":
                res_bat = pre_process_bat(n)[Index_of_interest_bats]
                res_pitch = pre_process_pitch(n)[Index_of_interest_pitcher]
            else:
                res_bat += pre_process_bat(n)[Index_of_interest_bats]
                res_pitch = (res_pitch + pre_process_pitch(n)[Index_of_interest_pitcher]).dropna()
        except:
            print("missing stats from {}".format(n))     

    res_bat["name"] = res_bat.index
    res_pitch["name"] = res_pitch.index
    # res_pitch["POS"] = res_pitch["POS"].apply(lambda x: x[:2])

    res_bat[Index_of_interest_bats] = res_bat[Index_of_interest_bats] /len(names)
    res_pitch[Index_of_interest_pitcher[1:]] = res_pitch[Index_of_interest_pitcher[1:]]/len(names)
    res_pitch.columns = ['POS', 'IP', 'H_p', 'HR_p', 'ER', 'BB_p', 'K_p', 'SV', 'HLD', 'QS', 'RAPP', "name"]
    res_bat.columns = ['PA', 'AB', 'H_b', '2B', '3B', 'HR_b', 'R', 'RBI', 'BB_b', 'K_b', 'HBP', 'SB', 'CS', "name"]
    res = res_bat.merge(res_pitch, how='outer').set_index("name")
    
    # try:
    #     teams =teams.applymap(lambda x: " ".join(x.split(" ")[:-3]) if x==x else np.nan).transpose()
    # except:   
    #     teams = pd.read_csv(root +  "/data/rosters.csv")
    #     teams =teams.applymap(lambda x: " ".join(x.split(" ")[:-3]) if x==x else np.nan).transpose()
    
    # team_col = []
    # for player in res.index:
    #     if sum((teams == player).sum(axis=1)) == 1:
    #         team_col.append(teams.index[np.argmax((teams == player).sum(axis=1))])
    #     else:
    #         team_col.append("FA")

    
    res["Teams"] = ['FA'] * len(res)

    for player in teams.index:
        if player in ['Mike Clevinger']:
            continue
        try:
            res.loc[player, 'Teams'] = teams.loc[player]
        except:
            # print(player)
            pass

    team_stats = res.groupby("Teams").agg("sum").drop("FA")

    team_raw_stats = team_stats
    team_stats['AVG'] = np.round(1000*team_raw_stats['H_b']/team_raw_stats['AB'])
    team_stats['OBP'] = (np.round(1000*(team_raw_stats['H_b']+team_raw_stats['HBP']+
                                        team_raw_stats['BB_b'])/team_raw_stats['PA']))
    team_stats['SLG'] = (np.round(1000*(3*team_raw_stats['HR_b']+
                                        2*team_raw_stats['3B']+
                                        team_raw_stats['2B']+
                                        team_raw_stats['H_b'])/team_raw_stats['AB']))
    team_stats['OPS'] = team_stats['SLG'] + team_stats['OBP']
    team_stats['NSB'] = team_raw_stats['SB'] - team_raw_stats['CS']
    team_stats['ERA'] = np.round(9*team_raw_stats['ER']/team_raw_stats['IP'], 2)
    team_stats['WHIP'] = np.round((team_raw_stats['H_p'] + team_raw_stats['BB_p'])/team_raw_stats['IP'], 2)
    team_stats['K/BB'] = np.round(team_raw_stats['K_p']/team_raw_stats['BB_p'], 2)
    team_stats['K/9'] = np.round(9*team_raw_stats['K_p']/team_raw_stats['IP'], 2)
    team_stats['BB/9'] = np.round(9*team_raw_stats['BB_p']/team_raw_stats['IP'], 2)
    team_stats['H/9'] = np.round(9*team_raw_stats['H_p']/team_raw_stats['IP'], 2)
    team_stats['NSV'] = team_raw_stats['SV']
    team_stats['NSVH'] = team_raw_stats['SV'] + team_raw_stats['HLD']

    Ranks_of_interest = ['IP', 'ERA', 'WHIP', 'K/9', 'BB/9', 'H/9', 'K/BB', 'NSV', 'NSVH', 'QS', 'RAPP',
                    'R', 'RBI', 'H_b', 'HR_b', 'K_b', 'BB_b', 'NSB', 'AVG', 'OBP', 'SLG', 'OPS']
    Asscending = [True, False, False, True, False, False, True, True, True, True, True,
            True, True, True, True, False, True, True, True, True, True, True]
    for stat,mask in  zip(Ranks_of_interest, Asscending):
        team_stats['r'+stat] = get_ranks(team_stats, stat, ascending=mask)

    rStats = list(map('r'.__add__,Ranks_of_interest))
    team_stats['POINTS'] = team_stats[rStats].sum(1)
    rStats.append('POINTS')
    
    return team_stats[rStats].sort_values("POINTS", ascending=False), res, team_stats[[s for s in team_stats if s not in rStats]]


def update_ranks():
    ranks = get_ranks_totales()
    teams = pd.read_csv(root +  "/data/teams.csv")
    teams =teams.applymap(lambda x: " ".join(x.split(" ")[:-3]) if x==x else np.nan).transpose()
    player_list = list(teams.values.reshape(-1))
    player_list = [i for i in player_list if i==i]
    ryu = player_list.index("Hyun Jin Ryu")
    player_list[ryu] = "Hyun-Jin Ryu"
    return ranks.loc[~ranks.index.isin(player_list)]

def best_pick_available(min_point = 50):
    team_ranks, res,_ = draft_companion()
    res = res[(res["SV"] + res["HLD"] > 10)|(res["PA"]>400)]
    fa_players = list(res[res["Teams"]=="FA"].index)
    fa_players = [p + " (Tm - POS)" for p in fa_players]
    teams = pd.read_csv(root + "/data/teams.csv")
    teams = teams[["Michel"] + [c for c in teams.columns if c!="Michel" ]]
    l = len(teams)
    ans = {}
    for player in fa_players:
        clear_output(wait=False)
        print(fa_players.index(player)+1, " of ", len(fa_players))
        teams.loc[l] = [player] + 11*[np.nan]
        x1,_, _ = draft_companion(teams)
        p = team_ranks.loc["Michel", "POINTS"]
        p1 = x1.loc["Michel", "POINTS"]
        ans[player] = p1-p
    return ans