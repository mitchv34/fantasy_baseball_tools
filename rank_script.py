import pandas as pd

def get_ranks_bats():
    
    names = ["steamer", "depthcharts", "razzball", "ATC", "thebat", "ZiPS"]

    col_names = []
    for n in names:
        print(n)
        try:
            if 'composite' in locals():
                pre_process_bat = pd.read_csv("data/proc/{}_bats.csv".format(n))
                composite = pd.merge(composite, pre_process_bat['POINTS'].to_frame(), how='inner', left_index=True, right_index=True)
            else:
                composite = pre_process_bat(n)["POINTS"].to_frame()            
            col_names.append(n)
        except:
            print("missing stats from {}".format(n))            

    composite['MEAN'] = composite.mean(axis=1)
    composite['VAR'] = composite.loc[:, composite.columns!="MEAN"].var(axis=1)
    composite.sort_values('MEAN', axis=0, ascending=False, inplace=True)

    composite.columns = ["Points_{}".format(i) for i in col_names] + ["MEAN", "VAR"]

    print(composite.head())
    return composite