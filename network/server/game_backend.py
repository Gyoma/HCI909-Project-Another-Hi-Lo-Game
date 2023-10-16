import os
import asyncio
from common.card import Card
from network.common.connection_command import ConnectionCommand

from network.server.player import Player
from common import constants

import random

class GameBackend:
    def __init__(self):
        self.players = {}
        self.command_handlers = {
            ConnectionCommand.Command.COMPETE.name : {
                'handler' : self.__compete_command,
                'sync' : asyncio.Barrier(constants.REQ_NUM_OF_PLAYERS),
                'req_opp' : True
            },
            ConnectionCommand.Command.USED_CARDS.name : {
                'handler' : self.__used_cards_command,
                'req_opp' : False
            }
        }

    async def player_connected(self, reader, writer):
        player_ip = writer.transport.get_extra_info('peername')[0] + str(random.randint(0, 1000))

        player = None

        # Check if data for this IP is present. If so, then we recover player state
        if player_ip in self.players:
            player = self.players.get(player_ip)
            
            # Cancel pending disconnection task
            if (player.disconnect_task is not None) and (not player.disconnect_task.cancelled()):
                try:
                    player.disconnect_task.cancel()
                finally:
                    pass

            player.reader = reader
            player.writer = writer
        else:
            # It's a new player or the player who reconnected after reconnection timeout fired
            player = Player(player_ip, reader, writer)
            self.players.update({player.ip : player})

        request = None

        while True:
            request = await reader.readline()
            request = request.decode('utf8').strip()

            # Client disconnected
            if not request:
                if (player.command_task is not None) and (not player.command_task.cancelled()):
                    try:
                        player.command_task.cancel()
                    finally:
                        pass
                
                break

            # If there is no pending command
            if (player.command_task is None) or (player.command_task.done()):
                def done_callback(task):
                    player.command_task = None

                    if task.cancelled():
                        return
                    
                    asyncio.create_task(self.__reply(writer, task.result()))

                command = ConnectionCommand.parse_command(request)

                player.command_task = asyncio.create_task(self.__handle_request(player, command))
                player.command_task.add_done_callback(done_callback)
                
                if command is not None:
                    player.command_task.set_name(command.name()) # just to make it more handy

            else:
                await self.__reply(writer, ConnectionCommand(ConnectionCommand.Command.STATUS, ['Waiting your opponent']))

        writer.close()
        await writer.wait_closed()

        # Creating timer task to remove player's data
        player.disconnect_task = asyncio.create_task(asyncio.sleep(constants.DISCONNECT_TIMEOUT_SEC))

        def disconnect_callback(task):
            player.disconnect_task = None

            if task.cancelled():
                return
            
            # print(f'Player\'s data removed for {player.ip}')
            
            self.players.pop(player.ip)

        player.disconnect_task.add_done_callback(disconnect_callback)
        

    async def __reply(self, writer, command):
        writer.write(command.pack())
        await writer.drain()

    async def __handle_request(self, player, command):
        if command is None:
            return ConnectionCommand(ConnectionCommand.Command.ERROR, ['Bad command'])
        
        return await self.command_handlers.get(command.name()).get('handler')(player, command.args())

    async def __compete_command(self, player, args):
        if len(args) != constants.REQ_NUM_OF_CARDS_FOR_ROUND:
            return ConnectionCommand(ConnectionCommand.Command.ERROR,
                [f'Req. num of cards is {constants.REQ_NUM_OF_CARDS_FOR_ROUND}, but got {len(cards)}'])

        cards = []

        for arg in args:
            if not self.__is_card(arg):
                return ConnectionCommand(ConnectionCommand.Command.ERROR, [f'Card is expected, but got {card}'])
            
            suit, rank = self.__get_suit_rank(arg)

            card = Card(Card.Suit[constants.FULL_SUITS[suit]], Card.Rank[constants.FULL_RANKS[rank]])

            if await player.card_used(card):
                return ConnectionCommand(ConnectionCommand.Command.ERROR, [f'Card is already used: {card}'])
            
            cards.append(card)
            
        player.set_cards(cards)
            
        await self.__reply(player.writer, ConnectionCommand(ConnectionCommand.Command.STATUS, ['Waiting your opponent']))

        barrier = self.command_handlers.get(ConnectionCommand.Command.COMPETE.name).get('sync')

        await barrier.wait()
        
        opponent = self.__get_opponent(player)

        if opponent is None:
            return ConnectionCommand(ConnectionCommand.Command.ERROR, ['No opponent found'])
        
        res = await player.compete(opponent)

        await barrier.wait()
        await player.update()

        if res == 1:
            return ConnectionCommand(ConnectionCommand.Command.COMPETE_RES, ['win'])
        if res == -1:
            return ConnectionCommand(ConnectionCommand.Command.COMPETE_RES, ['loss'])
        
        return ConnectionCommand(ConnectionCommand.Command.COMPETE_RES, ['draw'])

    async def __used_cards_command(self, player, args):
        if len(player.used_cards) == 0:
            return ConnectionCommand(ConnectionCommand.Command.ERROR, ['No used cards'])
        
        return ConnectionCommand(ConnectionCommand.Command.USED_CARDS_RES, player.used_cards)
    
    def __is_card(self, challenger):
        return challenger in constants.CARD_NAMES

    def __get_suit_rank(self, card):
        return card[0], card[1:]

    def __get_opponent(self, player):
        for key, value in self.players.items():
            if key != player.ip:
                return value
            
        return None