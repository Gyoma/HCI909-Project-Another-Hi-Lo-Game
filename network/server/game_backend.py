import os
import asyncio
from network.common.connection_command import ConnectionCommand

from network.server.player import Player
from network.common import server_constants
from network.common import server_helper

class GameBackend:
    def __init__(self):
        self.players = {}
        self.command_handlers = {
            ConnectionCommand.Command.COMPETE.name : {
                'handler' : self._compete_command,
                'sync' : asyncio.Barrier(server_constants.REQ_NUM_OF_PLAYERS),
                'req_opp' : True
            },
            ConnectionCommand.Command.USED_CARDS.name : {
                'handler' : self._used_cards_command,
                'req_opp' : False
            }
        }

    async def player_connected(self, reader, writer):
        player_ip = writer.transport.get_extra_info('peername')[0]

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
            if not request or request == 'quit':
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
                    
                    asyncio.create_task(self._reply(writer, task.result()))

                command = server_helper.parse_command(request)

                player.command_task = asyncio.create_task(self._handle_request(player, command))
                player.command_task.add_done_callback(done_callback)
                
                if command is not None:
                    player.command_task.set_name(command.name()) # just to make it more handy

            else:
                await self._reply(writer, ConnectionCommand(ConnectionCommand.Command.STATUS, ['Waiting your opponent']))

        writer.close()
        await writer.wait_closed()

        # Creating timer task to remove player's data
        player.disconnect_task = asyncio.create_task(asyncio.sleep(server_constants.DISCONNECT_TIMEOUT_SEC))

        def disconnect_callback(task):
            player.disconnect_task = None

            if task.cancelled():
                return
            
            # print(f'Player\'s data removed for {player.ip}')
            
            self.players.pop(player.ip)

        player.disconnect_task.add_done_callback(disconnect_callback)
        

    async def _reply(self, writer, command):
        writer.write(command.pack())
        await writer.drain()

    async def _handle_request(self, player, command):
        if command is None:
            return ConnectionCommand(ConnectionCommand.Command.RESULT, ['Bad command'])
        
        return await self.command_handlers.get(command.name()).get('handler')(player, command.args())

    async def _compete_command(self, player, cards):
        if len(cards) != server_constants.REQ_NUM_OF_CARDS:
            return ConnectionCommand(ConnectionCommand.Command.RESULT,
                [f'Req. num of cards is {server_constants.REQ_NUM_OF_CARDS}, but got {len(cards)}'])

        for card in cards:
            if not server_helper.is_card(card):
                return ConnectionCommand(ConnectionCommand.Command.RESULT, [f'Card is expected, but got {card}'])
            
            if await player.card_used(card):
                return ConnectionCommand(ConnectionCommand.Command.RESULT, [f'Card is already used: {card}'])
            
        player.set_cards(cards)
            
        await self._reply(player.writer, ConnectionCommand(ConnectionCommand.Command.STATUS, ['Waiting your opponent']))

        barrier = self.command_handlers.get(ConnectionCommand.Command.COMPETE.name).get('sync')

        await barrier.wait()
        
        opponent = self._get_opponent(player)

        if opponent is None:
            return ConnectionCommand(ConnectionCommand.Command.RESULT, 'No opponent found')
        
        res = await player.compete(opponent)

        await barrier.wait()
        await player.update()

        if res == 1:
            return 'win'
        if res == -1:
            return 'loss'
        
        return 'draw'

    async def _used_cards_command(self, player, args):
        if len(player.used_cards) == 0:
            return ConnectionCommand(ConnectionCommand.Command.RESULT, 'No used cards')
        
        return ConnectionCommand(ConnectionCommand.Command.RESULT, ' '.join(player.used_cards))

    def _get_opponent(self, player):
        for key, value in self.players.items():
            if key != player.ip:
                return value
            
        return None