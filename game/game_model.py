import asyncio
from common import constants
from common.card import Card
from enum import Enum

import itertools
from detector.threaded_card_detector import ThreadedCardDetector
from game.settings import Settings
from network.client.client import Client

from network.common.connection_command import ConnectionCommand
from network.server import server
from voice_recognition.voice_command_recognizer import VoiceCommandRecognizer, VoiceVocabulary, VoiceCommand

class GameModel():
    def __init__(self, event_loop, client_read_queue, client_write_queue):
        self.event_loop = event_loop
        self.client = Client(client_read_queue, client_write_queue)
        self.voice_recognizer = VoiceCommandRecognizer()
        self.card_detector = ThreadedCardDetector()
        self.settings = Settings()

        self.client_command_handlers = {
            ConnectionCommand.Command.COMPETE.name : self.__client_compete_command,
            ConnectionCommand.Command.COMPETE_RES.name : self.__client_compete_command_res,
            ConnectionCommand.Command.USED_CARDS.name : self.__client_used_cards_command,
            ConnectionCommand.Command.USED_CARDS_RES.name : self.__client_used_cards_command_res,
            ConnectionCommand.Command.STATUS.name : self.__client_status_command,
            ConnectionCommand.Command.ERROR.name : self.__client_error_command
        }

        self.voice_recognizer_command_handlers = {
            VoiceVocabulary.COMPETE.name : self._voice_compete_command
        }

        self.reset()

    def process_client_command(self, command):
        if (command is None) or (not command.name() in self.client_command_handlers):
            return
        
        self.client_command_handlers.get(command.name())(command)

    def process_voice_command(self, command : VoiceCommand):
        if (command is None) or (not command.name in self.voice_recognizer_command_handlers):
            return
        
        self.voice_recognizer_command_handlers.get(command.name)(command)

    def start_server(self):
        self.server_task = asyncio.run_coroutine_threadsafe(server.run_server(), self.event_loop)
        
    def connect(self, host = '127.0.0.1'):
        # Create connection coroutine in main thread

         # Wait for the server to start accepting connections. Need to be reviewed
        delay = 0

        if hasattr(self, "server_task"):
            delay = 3
        
        self.client_task = asyncio.run_coroutine_threadsafe(self.client.connect(host, delay),
                                                            self.event_loop)

    @classmethod
    def get_all_cards(cls):
        return [Card(suit, rank) for suit, rank in itertools.product(Card.Suit, Card.Rank)]
    

    def reset(self):
        self.rounds_left = constants.MAX_NUM_OF_ROUNDS
        self.round_result = None
        self.player_round_wins = 0
        self.player_round_losses = 0

        self.player_available_cards = self.get_all_cards()
        self.player_used_cards = []
        self.player_selected_cards = []
        self.opponent_selected_cards = []

    def __client_compete_command(self, command):
        cards = command.args()

        args = []
        for card in cards:
            suit, rank = card.split('-')
            args.append(constants.SHORT_SUITS[suit] + constants.SHORT_RANKS[rank])
        
        command = ConnectionCommand(command.command(), args)

        self.client.write_queue.sync_q.put(command)

    def __client_compete_command_res(self, command):
        status, opponent_cards = command.args()

        opponent_cards = opponent_cards.split('-')
        opponent_cards = [Card(Card.Suit[constants.FULL_SUITS[card[0]]], Card.Rank[constants.FULL_RANKS[card[1:]]]) for card in opponent_cards]

        self.opponent_selected_cards = opponent_cards

        self.rounds_left -= 1
        self.round_result = constants.RoundResult[status]

        match self.round_result:
            case constants.RoundResult.WIN:
                self.player_round_wins += 1
            case constants.RoundResult.LOSS:
                self.player_round_losses += 1

    def __client_used_cards_command(self, command):
        self.client.write_queue.sync_q.put(command)

    def __client_used_cards_command_res(self, command):
        pass

    def __client_status_command(self, command):
        print(str(command))

    def __client_error_command(self, command):
        print(str(command))

    def _voice_compete_command(self, command):
        args = [card.suit.name + '-' + card.rank.name for card in self.player_selected_cards]

        self.process_client_command(ConnectionCommand(ConnectionCommand.Command.COMPETE, args))

    