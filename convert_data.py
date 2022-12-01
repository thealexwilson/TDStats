import sys
import os
import csv
import pandas as pd
import re

def main():
    teams = []
    players = []
    with open("Teams.txt") as f:
        for line in f.readlines():
            line = line.strip()
            if ( line == "-----------------"):
                # next line is a team
                newTeam = True
            elif ( newTeam == True ):
                team = line.strip()
                teams.append(team)
                newTeam = False
            else:
                player = line.strip()
                players.append(player)

    stats_root = "Stats"
    for path, subdirs, files in os.walk(stats_root):
        for file_name in files:
            map_name = re.search("(?<=- ).*?(?=.csv)", file_name).group()
            match_name = re.search(".*?(?=.csv)", file_name).group()
            
            with open(os.path.join(path, file_name),'r') as csvinput:
                current_teams = []
                for match_row in csv.reader(csvinput):
                    if match_row:
                        team_row = match_row[0]
                        for team in teams:
                            if team == team_row:
                                current_teams.append(team_row)
                pretty_teams = '-'.join(list(dict.fromkeys(current_teams)))
            
            with open(os.path.join(path, file_name),'r') as csvinput:
                with open(f'converted_stats/{pretty_teams} {match_name}.csv', 'w') as csvoutput:
                    reader = csv.reader(csvinput)
                    writer = csv.writer(csvoutput, lineterminator='\n')

                    all = []
                    row = next(reader)
                    if row:
                        row.insert(0, "My Index")
                        all.append(row)

                        index = 0
                        for reader_row in reader:
                            if reader_row:
                                reader_row.insert(0, index)
                                index = index + 1
                                all.append(reader_row)

                    writer.writerows(all)
            
if __name__ == '__main__':
    main()