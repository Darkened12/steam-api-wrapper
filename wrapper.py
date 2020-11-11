import aiohttp


class Lobby:
    def __init__(self, steam_key, steam_profiles):
        """steam_profiles will contain a dict with {identifier: steam_id} structure"""
        self.STEAM_KEY = steam_key
        self.GET_SUMMARIES = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
        self.data = steam_profiles

    @staticmethod
    async def get_request(endpoint, credentials=None, mode='text'):
        """Asynchronous http get request method"""
        if credentials is None:
            credentials = {}
        async with aiohttp.ClientSession(headers={'Connection': 'keep-alive'}) as session:
            async with session.get(endpoint, params=credentials, timeout=7, allow_redirects=True) as resp:
                if mode == 'text':
                    return await resp.text()
                elif mode == 'json':
                    return await resp.json()
                else:
                    return await resp.read()

    @staticmethod
    async def convert_url_to_steamid(url, steam_key):
        """Parse a direct link to a profile or a steam custom name and returns its steamid64 number"""
        if '/' in url:
            if url[-1] == '/':
                url = url[:-1]
            url = url.split('/')[-1]
        if url.isdecimal():
            return url

        response = await Lobby.get_request(
            endpoint='http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/',
            credentials={'key': steam_key, 'vanityurl': url},
            mode='json'
        )
        return response['response']['steamid']

    async def get_single_user_data(self, steamid):
        """Gets a player's summary information without parsing"""
        response = await self.get_request(endpoint=self.GET_SUMMARIES,
                                     credentials={'key': self.STEAM_KEY, 'steamids': steamid},
                                     mode='json')
        try:
            return response['response']['players'][0]
        except IndexError:
            raise IndexError('steamid not found!')

    async def get_player_status(self, steamid):
        """Returns a more readable and more specific information about the given steam player"""
        player = await self.get_single_user_data(steamid)

        return {
            player['personaname']: {
                'playing': player['gameextrainfo'] if 'gameextrainfo' in player else False,
                'steamid': player['steamid'],
                'has_lobby': f'steam://joinlobby/{player["gameid"]}/{player["lobbysteamid"]}' if 'lobbysteamid' in player else False,
                'visibility': player['communityvisibilitystate']
            }
        }

    async def get_all_current_lobbies(self):
        """Gets all active lobbies from all users registered in steam_profiles"""
        players_id = [self.data[player] for player in self.data]
        response = await self.get_request(
            endpoint=f'{self.GET_SUMMARIES}?key={self.STEAM_KEY}&steamids={players_id}',
            mode='json'
        )
        steam_players = response['response']['players']
        lobbies = {}

        for player in steam_players:
            if 'lobbysteamid' in player:
                gameextrainfo = player['gameextrainfo']
                gameid = player['gameid']
                lobbysteamid = player['lobbysteamid']
                personaname = player['personaname']
                steamid = player['steamid']
                steam_lobby_link = f'steam://joinlobby/{gameid}/{lobbysteamid}'

                if gameextrainfo in lobbies:
                    if steam_lobby_link in lobbies[gameextrainfo]:
                        lobbies[gameextrainfo][steam_lobby_link].update({personaname: steamid})
                    else:
                        lobbies[gameextrainfo].update({steam_lobby_link: {personaname: steamid}})
                else:
                    lobbies.update({gameextrainfo: {steam_lobby_link: {personaname: steamid}}})

        return lobbies
