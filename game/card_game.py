import arcade
import asyncio

import threading

import cv2

from game.game_model import GameModel
from interface.game_window import GameWindow
from network.client.client import Client

from network.server import server

from interface.mainmenuview import MainMenuView

# Global variable
_game = None

def init(event_loop, client_read_queue, client_write_queue):
    global _game
    _game = Game(event_loop, client_read_queue, client_write_queue)

def game():
    return _game

class Game:
    def __init__(self, event_loop, client_read_queue, client_write_queue):
        self.model = GameModel(event_loop, client_read_queue, client_write_queue)

    def setup(self):
        self.window = GameWindow(self)
        self.window.show_view(MainMenuView())
        
    def run(self):
        arcade.run()

    def clean(self):
        cv2.destroyAllWindows()