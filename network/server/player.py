from common import constants

class Player:
    """
    Class representing a player on server side with corresponding data

    It stores all the data needed for the game and process it according to the game rules.
    """

    def __init__(self, ip, reader, writer):
        self.ip = ip
        self.used_cards = []
        self.curr_cards = []
        self.reader = reader
        self.writer = writer
        self.command_task = None
        self.disconnect_task = None
        self.rounds_left = constants.MAX_NUM_OF_ROUNDS

    def card_used(self, card):
        return self.cards_used([card])

    def cards_used(self, cards):
        return any([card in self.used_cards for card in cards])
    
    async def compete(self, player):
        beat = 0
        beaten = 0

        # Compare card's ranks in the corresponding order
        for my_card, other_card in zip(self.curr_cards, player.curr_cards):
            my_rank = constants.SHORT_RANKS[my_card.rank.name]
            other_rank = constants.SHORT_RANKS[other_card.rank.name]

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

    def update(self):
        self.rounds_left -= 1

        if self.rounds_left > 0:
            self.used_cards.extend(self.curr_cards)
        else:
            self.used_cards = []
            self.rounds_left = constants.MAX_NUM_OF_ROUNDS

        self.curr_cards = []