# Script parses a text file that contains a list of tournament team names and their players
# Assumptions about text file:
# Team name is on the next line after -----------------
# Player names are listed after their respective team names

import json

class Team:
    def __init__(self, name):
        self.Name = name
        self.Players = []
        return

    def addPlayer(self, player):
        player.setRank( len(self.Players) + 1 )
        self.Players.append( player )
        

class Player:
    def __init__(self, name) -> None:
        self.Name = name
        pass

    def setRank(self, rank ):
        self.Rank = rank
        return

def main():

    Teams = []
    newTeam = False

    with open("Teams.txt") as f:
        for line in f.readlines():
            line = line.strip()
            if ( line == "-----------------"):
                # next line is a team
                newTeam = True
            elif ( newTeam == True ):
                team = Team(line.strip())
                Teams.append( team )
                newTeam = False
            else:
                player = Player(line.strip())
                Teams[-1].addPlayer(player)

    printTeams( Teams )
    dumpTeams( Teams )

def printTeams( Teams ):
    print("Found teams: " + str(len(Teams)) )
    for team in Teams:
        print("Players in " + team.Name)
        for player in team.Players:
            print("Player#" + str(player.Rank) + ": \t " + player.Name )

def dumpTeams( Teams ):
    # the json file where the output must be stored
    with open("myfile.json", "w") as outFile:
        json.dump(Teams, outFile, default=lambda x: x.__dict__) 
                    
    return

if ( __name__ == "__main__" ):
    main()