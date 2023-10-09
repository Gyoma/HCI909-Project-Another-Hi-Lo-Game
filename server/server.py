import asyncio
from game_backend import GameBackend


async def main():
    backend = GameBackend()
    server = await asyncio.start_server(backend.player_connected, '', 3306)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())