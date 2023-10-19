import asyncio
import janus 
import time
import threading

from game import card_game

# Thread-safe queues supporting asyncio's coroutines approach for communication between threads
client_read_queue = None
client_write_queue = None
asyncio_initialized = False

def asyncio_init():
    global client_read_queue
    global client_write_queue
    global asyncio_initialized

    # Cannot be created outside of asyncio's running event loop
    client_read_queue = janus.Queue()
    client_write_queue = janus.Queue()
    asyncio_initialized = True
    
def asyncio_run(event_loop):
    asyncio.set_event_loop(event_loop)
    event_loop.call_soon(asyncio_init)
    event_loop.run_forever()

def main():
    global asyncio_initialized

    # Start asyncio event loop in another thread
    asyncio_event_loop = asyncio.new_event_loop()
    asyncio_thread = threading.Thread(target=asyncio_run, args=(asyncio_event_loop, ), daemon=True)
    asyncio_thread.start()

    # Wait til the asincio thread is initialized
    while not asyncio_initialized:
        time.sleep(0.2) # yield

    card_game.init(asyncio_event_loop, client_read_queue, client_write_queue)
    
    game = card_game.game()
    game.setup()
    game.run()
    game.clean()

if __name__ == "__main__":    
    main()
    