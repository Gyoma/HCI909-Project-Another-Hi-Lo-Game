import asyncio
from common import constants
from common.card import Card
from enum import Enum

import itertools
from network.client.client import Client

from network.common.connection_command import ConnectionCommand
from network.server import server

class GameModel():
    class Result(Enum):
        DRAW = 0
        FIRST_PLAYER_WINS = 1
        SECOND_PLAYER_WINS = 2

    def __init__(self, event_loop, client_read_queue, client_write_queue):
        self.event_loop = event_loop
        self.client = Client(client_read_queue, client_write_queue)
        
        self.player_available_cards = self.get_all_cards()
        self.player_used_cards = []
        self.player_selected_cards = []
        self.opponent_selected_cards = []

        self.command_handlers = {
            ConnectionCommand.Command.COMPETE.name : self.__compete_command,
            ConnectionCommand.Command.COMPETE_RES.name : self.__compete_command_res,
            ConnectionCommand.Command.USED_CARDS.name : self.__used_cards_command,
            ConnectionCommand.Command.USED_CARDS_RES.name : self.__used_cards_command_res,
            ConnectionCommand.Command.STATUS.name : self.__status_command
        }

    def process_command(self, command):
        if command is None:
            return
        
        self.command_handlers.get(command.name())(command)

    def start_server(self):
        self.server_task = asyncio.run_coroutine_threadsafe(server.run_server(), self.event_loop)
        
    def connect(self, host = '127.0.0.1'):
        # Create connection coroutine in main thread

         # Wait for the server to start accepting connections. Need to be reviewed
        delay = 0

        if hasattr(self, "server_task"):
            delay = 5
        
        self.client_task = asyncio.run_coroutine_threadsafe(self.client.connect(host, delay),
                                                            self.event_loop)

    @classmethod
    def get_all_cards(cls):
        return [Card(suit, rank) for suit, rank in itertools.product(Card.Suit, Card.Rank)]

    def __compete_command(self, command):
        cards = command.args()

        args = []
        for card in cards:
            suit, rank = card.split('-')
            self.player_selected_cards.append(Card(Card.Suit[suit], Card.Rank[rank]))
            args.append(constants.SHORT_SUITS[suit] + constants.SHORT_RANKS[rank])
        
        command = ConnectionCommand(command.command(), args)

        self.client.write_queue.sync_q.put(command)

    def __compete_command_res(self, command):
        pass

    def __used_cards_command(self, command):
        self.client.write_queue.sync_q.put(command)

    def __used_cards_command_res(self, command):
        pass

    def __status_command(self, command):
        print(command.pack())