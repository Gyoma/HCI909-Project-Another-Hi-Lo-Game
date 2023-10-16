import arcade
import asyncio

import threading

from game.gamemodel import GameModel
from network.client.client import Client

from network.server import server

from interface.mainmenuview import MainMenuView
from interface import uiconstants

_game = None

def init(event_loop, client_read_queue, client_write_queue):
    global _game
    _game = Game(event_loop, client_read_queue, client_write_queue)

def game():
    return _game

class Game:
    def __init__(self, event_loop, client_read_queue, client_write_queue):
        self.event_loop = event_loop
        self.model = GameModel()
        
        self.client = Client(client_read_queue, client_write_queue)

        self.__setup()

    def __setup(self):
        self.window = arcade.Window(uiconstants.WINDOW_WIDTH, uiconstants.WINDOW_HEIGHT, 
                                    title="Another Hi-Lo Game", resizable=True)
        
        self.window.set_min_size(uiconstants.MIN_WINDOW_WIDTH, uiconstants.MIN_WINDOW_HEIGHT)
        self.window.show_view(MainMenuView())

    def run(self):
        arcade.run()

    def clean(self):
        pass

    def start_server(self):
        self.server_task = asyncio.run_coroutine_threadsafe(server.run_server(), self.event_loop)
        
        
    def connect(self, host = '127.0.0.1'):
        # Create connection coroutine in main thread

         # Wait for server to start accepting connections. Need to be reviewed
        delay = 0

        if hasattr(self, "server_task"):
            delay = 5
        
        self.client_task = asyncio.run_coroutine_threadsafe(self.client.connect(host, delay),
                                                            self.event_loop)