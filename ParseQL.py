import requests
from bs4 import BeautifulSoup

#URL = "https://qlstats.net/game/8307697"

def ParseAndAddPlayers(players: dict, teamname: str, soup: BeautifulSoup):
    results = soup.find_all("tr", class_=teamname)

    for tr in results:
        tds = tr.find_all("td")
        if (len (tds) > 5 ):
            player = {}
            steamID = 0
            if ('href' in tds[0].contents[1].attrs):
                steamID = tds[0].contents[1].attrs["href"].split("/")[2]
            player["name"] = f"{tds[0].text}".strip()
            player["kills"] = f"{tds[2].text}"
            player["deaths"] = f"{tds[3].text}"
            
            players[steamID] = player

def ParseQLPage( URL: str ):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    players = {}

    ParseAndAddPlayers(players, "red", soup)
    ParseAndAddPlayers(players, "blue", soup)

    return players

def GetKD(players: dict, steamID: str):
    kills = 0
    deaths = 0
    if steamID in players.keys():
        kills = players[steamID]["kills"]
        deaths = players[steamID]["deaths"]
        
    return (kills, deaths)



