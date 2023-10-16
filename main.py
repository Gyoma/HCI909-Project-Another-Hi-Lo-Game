import asyncio
import janus 

from game import cardgame

def start_game(event_loop, client_read_queue, client_write_queue):
    cardgame.init(event_loop, client_read_queue, client_write_queue)
    
    game = cardgame.game()
    game.run()
    game.clean()

async def main():
    loop = asyncio.get_running_loop()

    client_read_queue = janus.Queue()
    client_write_queue = janus.Queue()

    await asyncio.to_thread(start_game, loop, client_read_queue, client_write_queue)

if __name__ == "__main__":    
    asyncio.run(main())