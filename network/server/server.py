import asyncio

from common import constants
from network.server.game_backend import GameBackend

async def run_server():
    print(f'Starting server on {constants.SERVER_PORT} port...')

    backend = GameBackend()
    server = await asyncio.start_server(backend.player_connected, 
                                        '', 
                                        constants.SERVER_PORT)
    
    print(f'Start listening on {constants.SERVER_PORT} port...')    
    async with server:
        await server.serve_forever()