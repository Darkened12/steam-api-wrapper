# steam-api-wrapper
Asynchronous wrapper to get info about users and their active lobbies

## Requirements:
aiohttp

## Usage example: 

```py
import asyncio
import json
from wrapper import Lobby


STEAM_KEY = ''  # Your API key

with open('steam_ids.json', 'r') as file:
    profiles = json.load(file)  # json with {'identifier': 'steam64id'} structure


async def main():
    lobby = Lobby(steam_key=STEAM_KEY, steam_profiles=profiles)
    id = await Lobby.convert_url_to_steamid('Lightsworn12', STEAM_KEY)  # Get the steam64 id necessary to use the wrapper
    print(await lobby.get_player_status(id))  # Get parsed basic information about a user
    print(await lobby.get_single_user_data(id))  # Get complete information about a user
    print(await lobby.get_all_current_lobbies())  # Get all active lobbies/rooms using the profiles dict


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
