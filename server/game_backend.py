import asyncio
import constants
from player import Player

class GameBackend:
    def __init__(self):
        # self.free_id = 0
        self.players = {}
        self.command_handlers = {
            'compete' : {
                'handler' : self._compete_command,
                'sync' : asyncio.Barrier(constants.REQ_NUM_OF_PLAYERS),
                'req_opp' : True
            },
            'used_cards': {
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

            if (player.command_task is None) or (player.command_task.done()):
                def done_callback(task):
                    if task.cancelled():
                        return
                    
                    asyncio.create_task(self._reply(writer, task.result()))

                command, args = await self._parse_command(request)

                player.command_task = asyncio.create_task(self._handle_request(player, command, args))
                player.command_task.add_done_callback(done_callback)
                player.command_task.set_name(command) # just to make it more handy

            else:
                await self._reply(writer, 'Waiting your opponent')

        writer.close()
        await writer.wait_closed()

        # Creating timer task to remove player's data
        player.disconnect_task = asyncio.create_task(asyncio.sleep(constants.DISCONNECT_TIMEOUT_SEC))

        def disconnect_callback(task):
            if task.cancelled():
                return
            
            print(f'Player\'s data removed for {player.ip}')
            
            self.players.pop(player.ip)

        player.disconnect_task.add_done_callback(disconnect_callback)
        

    async def _reply(self, writer, response):
        writer.write((str(response) + '\n').encode('utf8'))
        await writer.drain()

    async def _handle_request(self, player, command, args):
        if command is None:
            return 'Bad command'
        
        return await self.command_handlers.get(command).get('handler')(player, args)


    async def _parse_command(self, request):
        args = request.split(' ')
        command, args = args[0], args[1:]

        if not self._is_command(command):
            return None, None
        
        return command, args

    def _is_command(self, challenger):
        return challenger in self.command_handlers.keys()
    
    async def _is_card(self, challenger):
        return challenger in constants.CARD_NAMES

    async def _compete_command(self, player, cards):
        if len(cards) != constants.REQ_NUM_OF_CARDS:
            return f'Req. num of cards is {constants.REQ_NUM_OF_CARDS}, but got {len(cards)}'

        for card in cards:
            if not await self._is_card(card):
                return f'Card is expected, but got {card}'
            
            if await player.card_used(card):
                return f'Card is already used: {card}'
            
        player.set_cards(cards)
            
        await self._reply(player.writer, 'Waiting your opponent')

        barrier = self.command_handlers.get('compete').get('sync')

        await barrier.wait()
        
        opponent = self._get_opponent(player)

        if opponent is None:
            return 'No opponent found'
        
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
            return 'No used cards'
        
        return ' '.join(player.used_cards)


    def _get_opponent(self, player):
        for key, value in self.players.items():
            if key != player.ip:
                return value
            
        return None