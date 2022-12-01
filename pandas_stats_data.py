import sys
import os
import csv
import pandas as pd
import re

def main():    
    dfs = []
    converted_stats_root = "Stats"
    for path, subdirs, files in os.walk(converted_stats_root):
        for file_name in files:
            map_name = re.search("(?<=- ).*?(?=.csv)", file_name).group()

            with open(os.path.join(path, file_name),'r') as f:
                df = pd.read_csv(f, index_col=False)
                df_copy = df.copy()
                # Remove rows with no player data
                df_copy.dropna(subset = ['Kills'], inplace = True)
                # print("df_copy: ")
                # print(df_copy)
                teams = list(dict.fromkeys(df['Team Name'].tolist()))

                dfs.append({ "map": map_name, "teams": teams, "df": df_copy })

    # print("dfs: ")
    # print(dfs)
    return dfs

if __name__ == '__main__':
    main()