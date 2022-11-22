import requests
from bs4 import BeautifulSoup

#URL = "https://qlstats.net/game/8307697"

def ParseAndAddPlayers(players: dict, teamname: str, soup: BeautifulSoup):
    results = soup.find_all("tr", class_=teamname)
    print("soup:")
    print(soup)
    print("results:")
    print(results)
    header_list = "nick", "time", "kills", "deaths", "score"
    # headers = soup.find_all("tr")
    # header for header in headers if header.text in header_list:
    ths = soup.find_all("th")
    print("ths:")
    print(ths)
    th_map = {}
    for th in ths:
        print("th:")
        print(th)
        if th.text in header_list:
            th_map[th.text] = th.text
    for tr in results:
        tds = tr.find_all("td")
        if (len (tds) > 5 ):
            player = {}
            steamID = tds[0].contents[1].attrs["href"].split("/")[2]
            player["name"] = f"{tds[0].text}".strip()
            player["kills"] = f"{tds[3].text}"
            player["deaths"] = f"{tds[4].text}"
            
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
    # TODO: Remove this
    # print("players:")
    # print(players)
    # print("kills")
    # print(kills)
    # print("deaths")
    # print(deaths)
    return (kills, deaths)



