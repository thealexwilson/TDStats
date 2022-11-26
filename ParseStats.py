import sys
import urllib.request, json
import csv
from types import SimpleNamespace
import jsonpickle
import os
import ParseQL

#sampleurl - "args": ["https://qlstats.net/game/7495401.json"]
GAMEURL = "https://qlstats.net/game/7650424"
TEXTFILE = "maps.txt"

AllPlayers = []
TournamentTeams = []

class TournamentTeam:
    def __init__(self, name):
        self.Name = name
        self.Players = []
        return

    def addPlayer(self, player):
        player.setRank( len(self.Players) + 1 )
        self.Players.append( player )
        

class TournamentPlayer:
    def __init__(self, name) -> None:
        self.Name = name
        pass

    def setRank(self, rank ):
        self.Rank = rank
        return

def LoadTournamentTeams():
    # Method parses a text file that contains a list of tournament team names and their players
    # Assumptions about text file:
    # Team name is on the next line after -----------------
    # Player names are listed after their respective team names

    global TournamentTeams

    newTeam = False

    with open("Teams.txt") as f:
        for line in f.readlines():
            line = line.strip()
            if ( line == "-----------------"):
                # next line is a team
                newTeam = True
            elif ( newTeam == True ):
                team = TournamentTeam(line.strip())
                TournamentTeams.append( team )
                newTeam = False
            else:
                player = TournamentPlayer(line.strip())
                TournamentTeams[-1].addPlayer(player)

def GetPlayerRank( player ):
    for team in TournamentTeams:
        for tournamentPlayer in team.Players:
            if ( player.Name.upper() == tournamentPlayer.Name.upper() ):
                return tournamentPlayer.Rank

    print("Could not find player " + player.Name + " registered in the tournament. Fix PlayerIDs.json")
    return 0

def GetPlayerTeamName( player ):
    for team in TournamentTeams:
        for tournamentPlayer in team.Players:
            if ( player.Name.upper() == tournamentPlayer.Name.upper() ):
                return team.Name

    print("Could not find player " + player.Name + " registered in the tournament. Fix PlayerIDs.json")
    return ""

def GetAllTournamentPlayersFromTeam( teamName ):
    for team in TournamentTeams:
        if ( teamName.upper() == team.Name.upper() ):
            return team.Players

    print("Could not find team " + teamName + " registered in the tournament.")
    return []


class Team():
    def __init__(self):
        self.Players = []
        self.Name = ""

    def addPlayer( self, player ):
        if ( player.ID == - 1 ):
            print( "Verify whether anonymous player is truly " + player.Name )
        rank = GetPlayerRank( player)
        if ( rank == 0 ):
            print("Please fix above problem before continuing")

        player.setRank( rank )

        teamName = GetPlayerTeamName( player )
        if ( len(self.Name) == 0 ):
            self.Name = teamName

        self.Players.append( player )
        self.Players.sort()

    def addName( self, name ):
        self.Name = name

    def addMissingPlayers( self ):
        AllTeamPlayers = []
        AllTeamPlayers = GetAllTournamentPlayersFromTeam( self.Name )
        for player in AllTeamPlayers:
            if ( self.isPlayerInCurrentMap( player.Name ) == False ):
                self.addPlayer( Player(0, player.Name) )
        return

    def isPlayerInCurrentMap( self, name ):
        found = False
        for player in self.Players:
            if ( name.upper() == player.Name.upper() ):
                found = True

        return found

class PlayerIDName():
    def __init__(self, id, name ):
        self.ID = id
        self.Name = name

    def encode(self):
        return self.__dict__

class WeapDamage():
    def __init__( self, damage, kills, shots, hits ):
        self.Damage = damage
        self.Kills = kills
        self.Shots = shots
        self.Hits = hits

class Player():
    def __init__( self, id, name ):
        self.ID = id
        self.Name = name
        self.Rank = 0 #Need to set correct ranks eventually
   
    def addKD( self, kills, deaths ):
        self.Kills = kills
        self.Deaths = deaths
    
    def addKDR( self, kills, deaths ):
        self.KDR = str(int(kills) - int(deaths))
       
    def addDamage( self, dealt, received ):
        self.DamageDealt = dealt
        self.DamageReceived = received

    def addNetDamage( self, dealt, received ):
        self.NetDamage = str(int(dealt) - int(received))

    def addWeapDamage( self, weap, damage, kills, shots, hits ):
        damage = WeapDamage( damage, kills, shots, hits )
        if weap == "rl":
            self.RLStats = damage
        elif weap == "gl":
            self.GLStats = damage
        elif weap == "pg":
            self.PGStats = damage
        elif weap == "sg":
            self.SGStats = damage
        elif weap == "rg":
            self.RGStats= damage
        elif weap == "lg":
            self.LGStats = damage
        elif weap == "hmg":
            self.HMGStats = damage
        elif weap == "mg":
            self.MGStats = damage

        # Player kills is sum of allkills
        if hasattr(self, "Kills") :
            self.Kills = self.Kills + kills
        else:
            self.Kills = kills
        

    def setRank( self, rank ):
        self.Rank = rank

    def __lt__(self, other):
        # This allows us to sort the players as per their rank
         return self.Rank < other.Rank

class Map():
    def __init__( self, name, date ):
        self.Name = name
        self.Date = date[0:10]
        self.Teams = [Team(), Team()]
        
    def addPlayer( self, id, player ):
        if id > 2:
            print("Error. How did we find a player with Team ID: " + str(id) )
            exit(2)

        self.Teams[id].addPlayer( player )

def main():
    global TEXTFILE

    if ( len(sys.argv) < 2 ):
        print( "Usage: StatsParser.py <Text file with QLStats links>")
        print( "  This will fetch the stats in a JSON format from the URLs")
        print( "  provided in a text file. (default = maps.txt")
        print( "  Stats will be parsed and produce a CSV file per map")
        print( "  Needs all tournament players to be listed in a Teams.txt file")
        print( "  Script will populate a PlayerIDs.json file with name retrieved from QLStats corresponding to an ID.")
        print("   Update this json file with correct registered player name as there are too many aliasing bastards")

        fileName = TEXTFILE
    else:
        fileName = sys.argv[1]

    try:
        with open(fileName) as file:
            for line in file.readlines():
                line = line.strip()
                if ( "json" not in line ):
                    line = line + ".json"
                
                parseStats( line )
    except FileNotFoundError:
        pass

# Not used anymore. This was the old way of doing things where you can provide a single qlstats URL
def main2():
    global GAMEURL

    if ( len(sys.argv) < 2 ):
        print( "Usage: StatsParser.py <QL-Stats-game-url.json>")
        print( "  This will fetch the stats in a JSON format from the URL")
        print( "  Parse it and produce a CSV file")
        print( "  Needs all tournament players to be listed in a Teams.txt file")
        print( "  Script will populate a PlayerIDs.json file with name retrieved from QLStats corresponding to an ID.")
        print("   Update this json file with correct registered player name as there are too many aliasing bastards")

        gameURL = GAMEURL
        if ( "json" not in gameURL ):
            gameURL = gameURL + ".json"
    else:
        gameURL = sys.argv[1]

    parseStats( gameURL )

# Main method to parse game stats and dump it to a csv file for a given URL
def parseStats( gameURL ):
    LoadTournamentTeams()
    LoadPlayers()

    with urllib.request.urlopen(gameURL) as url:
        data = json.loads(url.read().decode())
        print(data)
        parseGameStats(data, gameURL)

    DumpPlayers()

def LoadPlayers():
    global AllPlayers

    try:
        with open('PlayerIDs.json') as json_file:
            text = json.load(json_file, object_hook=lambda d: SimpleNamespace(**d))
            AllPlayers = jsonpickle.decode(text)
    except FileNotFoundError:
        pass

    print("Loaded " + str(len(AllPlayers)) + " players")
    return

def DumpPlayers():
    with open('PlayerIDs.json', 'w') as outfile:
        #json.dump(AllPlayers, outfile, default=lambda o: o.encode())
        print("Encode Object into JSON formatted Data using jsonpickle")
        allPlayersJSON = jsonpickle.encode(AllPlayers)
        json.dump(allPlayersJSON, outfile)
       

    print("Dumped " + str(len(AllPlayers)) + " players")
    return

def getPlayerName( playerID ):
    for player in AllPlayers:
        if ( player.ID == playerID ):
            return player.Name

    # Player name not yet discovered
    playerName = getPlayerNameFromQLStats( playerID )
    item = PlayerIDName( playerID, playerName )
    AllPlayers.append( item )
    return playerName

def getPlayerNameFromQLStats( playerID ):
    playerName = ""
    playerURL = "https://qlstats.net/player/" + str(playerID) + ".json"

    if playerID == -1:
        playerName = "CHA1N"
        return playerName

    with urllib.request.urlopen(playerURL) as url:
        data = json.loads(url.read().decode())

    playerName = data[0]['player']['stripped_nick']
    print("Retrieved Player from QL Stats: ID - " + str(playerID) + " Name - " + playerName )
    return playerName

def parseGameStats( data, gameURL:str ):
    mapName = data['map']['name']
    mapDate = data['game']['start']
    map = Map(mapName, mapDate)

    # TODO - Parse the QL page and load it into a dictionary
    QLPlayers = {}
    QLPlayers = ParseQL.ParseQLPage(gameURL.rstrip(".json"))

    for item in data['pgstats']:
        playerName = getPlayerName(item['player_id'])
        player = Player(item['player_id'], playerName )
        teamID = item['team'] - 1
        player.addDamage( item['pushes'], item['destroys'] )
        player.addNetDamage( item['pushes'], item['destroys'] )
        map.addPlayer( teamID, player )

    for item in data['pwstats']:
        player = getPlayerFromMap(map, int(item))
        for weapon in data['pwstats'][item]['weapons']:
            weaponDMG = data['pwstats'][item]['weapons'][weapon]
            player.addWeapDamage( weapon, weaponDMG[1], weaponDMG[0], weaponDMG[3], weaponDMG[2])

        #TODO - Get player KD
        kills = 0
        deaths = 0
        (kills, deaths) = ParseQL.GetKD(QLPlayers, item)
        player.addKD( kills, deaths)
        player.addKDR( kills, deaths )

    map.Teams[0].addMissingPlayers()
    map.Teams[1].addMissingPlayers()
    
    printAllPlayers( map )
    outputCSV(map)

def getPlayerFromMap( map, id ):
    for player in map.Teams[0].Players:
        if id == player.ID:
            return player

    for player in map.Teams[1].Players:
        if id == player.ID:
            return player

    print(" Could not find player with id: " + id )

def printAllPlayers( map ):
    print("===============================")
    print ( map.Name )
    print("")
    printTeamPlayers( map.Teams[0].Players )
    printTeamPlayers( map.Teams[1].Players )
    print("")
    print("===============================")


def printTeamPlayers( teamPlayers ):
    for player in teamPlayers:
        print( "ID: " + str(player.ID) + "\tName: " + str(player.Name))
       
        if ( hasattr(player, 'RLStats') ) :
            print( "  ----- RL Stats: " )
            weapStat = player.RLStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'GLStats') ):
            print( "  ----- GL Stats: " )
            weapStat = player.GLStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'LGStats') ):
            print( "  ----- LG Stats: " )
            weapStat = player.LGStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'RGStats') ):
            print( "  ----- RG Stats: " )
            weapStat = player.RGStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'SGStats') ):
            print( "  ----- SG Stats: " )
            weapStat = player.SGStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'PGStats') ):
            print( "  ----- PG Stats: " )
            weapStat = player.PGStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))

        if ( hasattr(player, 'MGStats') ) :
            print( "  ----- MG Stats: " )
            weapStat = player.MGStats
            print(" \t " + str(weapStat.Damage) + "\t" + str(weapStat.Shots) + "\t" + str(weapStat.Hits))


def outputCSV( map ):
    folderName = "Stats/" + map.Teams[0].Name[:5] + " v " + map.Teams[1].Name[:5]
    os.makedirs( folderName, exist_ok = True )
    outfileName = folderName + "/" + map.Date + " - " + map.Name + ".csv"
    with open(outfileName, 'w') as outfile:
        writeHeader2( outfile )
        writePlayerStats( map, outfile )

    return

def writeHeader( outFile ):
    header = ["Team Name", "Player Name", "Kills", "Deaths", "KDR", "Damage Dealt", "Damage Taken", "Net Damage", "MG Hits", "MG Shots", "MG acc", "SG Hits", "SG Shots", "GL Hits", "GL Shots",
               "RL Hits", "RL Shots", "LG Hits", "LG Shots","RG Hits", "RG Shots", "HMG Hits", "HMG Shots", "PG Hits", "PG Shots"]
    outFile.write( ','.join(header))
    outFile.write("\n")
    return

def writeHeader2( outFile ):
    header = ["Team Name", "Player Name", "Kills", "Deaths", "KDR", "Damage Dealt", "Damage Taken", "Net Damage", "MG Hits", "MG Shots", "MG acc", "SG Hits", "SG Shots", "SG acc", "GL Hits", "GL Shots",
              "GL Acc", "RL Hits", "RL Shots", "RL Acc", "LG Hits", "LG Shots", "LG Acc", "RG Hits", "RG Shots", "RG Acc",  "HMG Hits", "HMG Shots"
              , "HMG Acc", "PG Hits", "PG Shots", "PG Acc"]
    outFile.write( ','.join(header))
    outFile.write("\n")
    return

def writePlayerStats( map, outFile ):
    writeTeamStats( map.Teams[0].Name, map.Teams[0].Players, outFile )
    outFile.write("\n")
    writeTeamStats( map.Teams[1].Name, map.Teams[1].Players, outFile  )
    outFile.write("\n")

def writeTeamStats( teamName, players, outFile ):
    for player in players:

        line = teamName + ","
        line = line + player.Name + ","

        line = line + addAttr( player, 'Kills')
        line = line + addAttr( player, 'Deaths')
        line = line + addAttr( player, 'KDR')
        line = line + addAttr( player, 'DamageDealt')
        line = line + addAttr( player, 'DamageReceived')
        line = line + addAttr( player, 'NetDamage')
        line = line + addWeap2( player, 'MGStats')
        line = line + addWeap2( player, 'SGStats')
        line = line + addWeap2( player, 'GLStats')
        line = line + addWeap2( player, 'RLStats')
        line = line + addWeap2( player, 'LGStats')
        line = line + addWeap2( player, 'RGStats')
        line = line + addWeap2( player, 'HMGStats')
        line = line + addWeap2( player, 'PGStats')
       
        outFile.write(line)
        outFile.write("\n")
    return

def addAttr( obj, attr ):
    if ( hasattr(obj, attr) ) :
        line = str(getattr(obj, attr) ) + ","
    else:
        line = ","

    return line

def getWeapKills( obj, attr) :
    if ( hasattr(obj, attr)) :
        damage = getattr(obj, attr )
        return damage.Hits

    return 0

def addWeap( obj, attr ):
    if ( hasattr(obj, attr) ) :
        damage = getattr(obj, attr )

        line = str(damage.Hits)
        line = line + "," + str(damage.Shots) + ","
    else:
        line = ",,"
   
    return line

def addWeap2( obj, attr ):
    if ( hasattr(obj, attr) ) :
        damage = getattr(obj, attr )

        if ( damage.Shots == 0 ):
            line = ",,,"
            return line

        acc = round(damage.Hits*100/damage.Shots)
        line = str(damage.Hits)
        line = line + "," + str(damage.Shots)
        line = line + "," + str(acc) + "%,"
    else:
        line = ",,,"
   
    return line

if ( __name__ == "__main__" ):
    main()