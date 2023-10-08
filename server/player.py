import constants

class Player:
    def __init__(self, ip, reader, writer):
        self.ip = ip
        self.used_cards = []
        self.curr_cards = []
        self.reader = reader
        self.writer = writer
        self.command_task = None
        self.disconnect_task = None

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

            my_rank = constants.RANK_VALUES[my_rank]
            other_rank = constants.RANK_VALUES[other_rank]

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