import requests
from bs4 import BeautifulSoup

URL = "https://qlstats.net/game/8307697"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")


def PrintTeamDeaths(teamname: str):
    results = soup.find_all("tr", class_=teamname)
    for tr in results:
        tds = tr.find_all("td")
        if (len (tds) > 5 ):
            name = f"{tds[0].text}".strip()
            deaths = f"{tds[4].text}"
            print(name + " - " + deaths)

PrintTeamDeaths("red")
PrintTeamDeaths("blue")

