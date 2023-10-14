import asyncio
from game_backend import GameBackend


async def main():
    print('Starting server...')

    backend = GameBackend()
    port = 3306
    server = await asyncio.start_server(backend.player_connected, '', port)
    
    print(f'Start listening on {port} port...')    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())