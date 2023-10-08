import asyncio
import signal

REQ_NUM_OF_PLAYERS = 2

CARD_NAMES = ['H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK', 'HA', 
              'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'SJ', 'SQ', 'SK', 'SA',  
              'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK', 'CA', 
              'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'DJ', 'DQ', 'DK', 'DA']

RANK_VALUES = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}

class Player:
    def __init__(self, id, reader, writer) -> None:
        self.id = id
        self.used_cards = []
        self.curr_cards = []
        self.reader = reader
        self.writer = writer

    async def card_used(self, card):
        return await self.cards_used([card])

    async def cards_used(self, cards):
        return any([card in self.used_cards for card in cards])
    
    async def compete(self, player):
        beat = 0
        beaten = 0

        for my_card, other_card in zip(self.curr_cards, player.curr_cards):
            _, my_rank = self._get_suit_rank(my_card)
            _, other_rank = self._get_suit_rank(other_card)

            my_rank = RANK_VALUES[my_rank]
            other_rank = RANK_VALUES[other_rank]

            if my_rank > other_rank:
                beat += 1
            elif other_rank > my_rank:
                beaten += 1

        if beat > beaten:
            return 1 # I won
        if beaten > beat:
            return -1 # Opponent won
        return 0 # Draw
    
    def set_cards(self, cards):
        self.curr_cards = cards

    async def update(self):
        self.used_cards.extend(self.curr_cards)
        self.curr_cards = []

    def _get_suit_rank(self, card):
        return card[0], card[1:]


class GameBackend:
    def __init__(self) -> None:
        self.free_id = 0
        self.players = {}
        self.command_handlers = {
            'compete' : {
                'handler' : self._compete_command,
                'sync' : asyncio.Barrier(REQ_NUM_OF_PLAYERS)
            },
            'used_cards': {
                'handler' : self._used_cards_command
            }
        }

    async def player_connected(self, reader, writer):
        player = Player(self.free_id, reader, writer)
        
        self.free_id += 1
        self.players.update({player.id : player})

        handler_task = None
        request = None

        while True:
            request = await reader.readline()
            request = request.decode('utf8').strip()

            # Client disconnected
            if not request or request == 'quit':
                if (handler_task is not None) and (not handler_task.cancelled()):
                    try:
                        handler_task.cancel()
                    finally:
                        pass
                break

            if (handler_task is None) or (handler_task.done()):
                def done_callback(task):
                    if task.cancelled():
                        return
                    
                    asyncio.create_task(self._reply(writer, task.result()))

                handler_task = asyncio.create_task(self._handle_request(player, request))
                handler_task.add_done_callback(done_callback)

            else:
                await self._reply(writer, 'Waiting your opponent')

        writer.close()
        await writer.wait_closed()
        self.players.pop(player.id)

    async def _reply(self, writer, response):
        writer.write((str(response) + '\n').encode('utf8'))
        await writer.drain()

    async def _handle_request(self, player, request):
        command, args = await self._parse_command(request)

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
        return challenger in CARD_NAMES

    async def _compete_command(self, player, cards):
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
            return 'loose'
        
        return 'draw'

    async def _used_cards_command(self, player, args):
        if len(player.used_cards) == 0:
            return 'No used cards'
        
        return ' '.join(player.used_cards)


    def _get_opponent(self, player):
        for key, value in self.players.items():
            if key != player.id:
                return value
            
        return None

async def main():
    backend = GameBackend()
    server = await asyncio.start_server(backend.player_connected, '127.0.0.1', 3306)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())