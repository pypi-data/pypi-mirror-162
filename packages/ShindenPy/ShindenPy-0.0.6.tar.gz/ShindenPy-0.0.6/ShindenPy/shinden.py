from aiohttp import ClientSession, TCPConnector, FormData
from asyncio import run, sleep, gather
from random  import randint
from json    import loads, dumps
from bs4     import BeautifulSoup, NavigableString
from re      import findall
from base64  import b64decode

shindenHeaders = {
    "accept-language": "en-US,en;q=0.9,pl;q=0.8",
    "user-agent"     : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

def pa(li):
    print("[")
    for x in li: print(' '*4 + str(x))
    print("]")

class Shinden():
    aiohttpSession = None
    # base64 encoded user auth key default "_guest_:0,5,21000000,255,4174293644"
    # Structure "NICKNAME:USERID,5,DATE,3,UNKNOWN"
    api4Auth = "X2d1ZXN0XzowLDUsMjEwMDAwMDAsMjU1LDQxNzQyOTM2NDQ"
    username = None
    userId   = None
    
    def __init__(self):
        self.aiohttpSession = ClientSession(
            connector=TCPConnector(limit=1)
        )

    async def close(self):
        await self.aiohttpSession.close()
    
    async def login(self, username, password):
        html = None

        formData = {
            "username": username,
            "password": password
        }

        async with self.aiohttpSession.post(f"https://shinden.pl/main/0/login", data=formData, headers={"referer":"https://shinden.pl/main/0/login"}) as r:
            html = await r.text()

        bf = BeautifulSoup(html, 'html.parser')
        scripts = bf.find_all('script', type="text/javascript")

        for script in scripts:
            basic = findall("_Storage.basic =  '.*'", script.text)
            if len(basic) != 0: self.api4Auth = basic[0].split("'")[1]

        self.username, self.userId = str(b64decode(self.api4Auth)).split(',')[0].split(':')

        print(f"[*] Changed auth token to '{self.api4Auth}'")

        return html

    async def searchAnime(self, name):
        name = name.replace(' ', '+')
        html = None

        async with self.aiohttpSession.get(f"https://shinden.pl/series?search={name}", headers=shindenHeaders) as r:
            html = await r.text()

        bf = BeautifulSoup(html, 'html.parser')
        animeList = bf.find_all("ul", class_="div-row")[1:]
        result = []
        for anime in animeList:
            result.append({
                "name": ' '.join(anime.contents[3].h3.a.stripped_strings),
                "url" : anime.contents[3].h3.a.get("href")
            })
        return result

    async def getEpisodePlayers(self, episodeUrl):
        html = None

        async with self.aiohttpSession.get(f"https://shinden.pl{episodeUrl}", headers=shindenHeaders) as r:
            html = await r.text()

        bf = BeautifulSoup(html, 'html.parser')
        players = bf.find_all("a", attrs={"href": "#column-one-inner"})
        return [ loads(player.get("data-episode")) for player in players]


    async def getAnimeEpisodes(self, anime):
        html = None

        #58136-shingeki-no-kyojin-the-final-season-2022
        async with self.aiohttpSession.get(f"https://shinden.pl/{anime}/all-episodes", headers=shindenHeaders) as r:
            html = await r.text()

        bf = BeautifulSoup(html, 'html.parser')
        episodeList = bf.find("tbody", class_="list-episode-checkboxes")
        episodes = []
        for episode in episodeList.children:
            if isinstance(episode, NavigableString):
                continue
            
            pa(episode.contents)
            episodes.append({
                "number": episode.contents[1].string,
                "title": episode.contents[3].string,
                "date": episode.contents[9].string,
                "url": episode.contents[11].a.get('href')
            })

        return episodes
    
    async def playerLoad(self, id, rw=False):
        if rw: await sleep( randint(0, 500) / 100 )
        async with self.aiohttpSession.get(f"https://api4.shinden.pl/xhr/{id}/player_load?auth={self.api4Auth}") as r:
            return await r.text()

    async def playerShow(self, id, rw=False):
        if rw: await sleep( randint(0, 500) / 100 )
        async with self.aiohttpSession.get(f"https://api4.shinden.pl/xhr/{id}/player_show?auth={self.api4Auth}") as r:
            return await r.text()

    async def getPlayer(self, id, rw=False):
        timeToWait = await self.playerLoad(id, rw)

        if timeToWait == "": return "Failed"
        await sleep(int(timeToWait) + (randint(0, 500)/100 if rw else 0))

        html =  await self.playerShow(id, rw)
        if len(html) < 10: return "failed"
        return BeautifulSoup(html, 'html.parser').find('iframe').get('src')
    
    async def getAnimeListAll(self):
        html = None

        #58136-shingeki-no-kyojin-the-final-season-2022
        async with self.aiohttpSession.get(f"https://shinden.pl/animelist/{self.userId}-{self.username}/all", headers=shindenHeaders) as r:
            html = await r.text()

        bf = BeautifulSoup(html, 'html.parser')

        animes = {
            'inProgress': [],
            'watched'   : [],
            'skipped'   : [],
            'onHold'    : [],
            'dropped'   : [],
            'planned'   : []
        }

        def animesFromAnimeList(animeList):
            result = []
            for anime in animeList.contents:
                if isinstance(anime, NavigableString): continue
                result.append({
                    "title"   : anime.contents[2].text.strip(),
                    "type"    : anime.contents[6].text.strip(),
                    "progress": anime.contents[5].text.strip(),
                    "rating"  : None if (tmp := anime.contents[3].text.strip()) == '?' else tmp,
                })
            return result

        animeList = bf.find("table", class_="section-in-progress", id="ver-zebra")
        if animeList is not None: animes['inProgress'] = animesFromAnimeList(animeList.tbody)

        animeList = bf.find("table", class_="section-completed", id="ver-zebra")
        if animeList is not None: animes['watched'] = animesFromAnimeList(animeList.tbody)

        animeList = bf.find("table", class_="section-skip", id="ver-zebra")
        if animeList is not None: animes['skipped'] = animesFromAnimeList(animeList.tbody)

        animeList = bf.find("table", class_="section-hold", id="ver-zebra")
        if animeList is not None: animes['onHold'] = animesFromAnimeList(animeList.tbody)

        animeList = bf.find("table", class_="section-dropped", id="ver-zebra")
        if animeList is not None: animes['dropped'] = animesFromAnimeList(animeList.tbody)

        animeList = bf.find("table", class_="section-plan", id="ver-zebra")
        if animeList is not None: animes['planned'] = animesFromAnimeList(animeList.tbody)
        
        return animes
