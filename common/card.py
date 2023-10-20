from enum import Enum

class Card():
    """
    A structure that represents a card.

    It's a wrapper around two enums: Suit and Rank.
    """

    class Suit(Enum):
        CLUBS = 1 # ♣
        DIAMONDS = 2 # ♦
        HEARTS = 3 # ♥
        SPADES = 4 # ♠

        def __str__(self):
            return self.name

    class Rank(Enum):
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        JACK = 11
        QUEEN = 12
        KING = 13
        ACE = 14

        def __str__(self):
            return self.name

    def __init__(self, suit : Suit, rank : Rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank
