from enum import Enum

class Card():
    class Suit(Enum):
        CLUBS = 1 # ♣
        DIAMONDS = 2 # ♦
        HEARTS = 3 # ♥
        SPADES = 4 # ♠

        def __str__(self):
            match (self):
                case Card.Suit.CLUBS:
                    return "Clubs"
                case Card.Suit.DIAMONDS:
                    return "Diamonds"
                case Card.Suit.HEARTS:
                    return "Hearts"
                case Card.Suit.SPADES:
                    return "Spades"
                
        @classmethod
        def from_str(cls, suit_str):
            match (suit_str):
                case "Clubs":
                    return Card.Suit.CLUBS
                case "Diamonds":
                    return Card.Suit.DIAMONDS
                case "Hearts":
                    return Card.Suit.HEARTS
                case "Spades":
                    return Card.Suit.SPADES

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
            match (self):
                case Card.Rank.TWO:
                    return "2"
                case Card.Rank.THREE:
                    return "3"
                case Card.Rank.FOUR:
                    return "4"
                case Card.Rank.FIVE:
                    return "5"
                case Card.Rank.SIX:
                    return "6"
                case Card.Rank.SEVEN:
                    return "7"
                case Card.Rank.EIGHT:
                    return "8"
                case Card.Rank.NINE:
                    return "9"
                case Card.Rank.TEN:
                    return "10"
                case Card.Rank.JACK:
                    return "J"
                case Card.Rank.QUEEN:
                    return "Q"
                case Card.Rank.KING:
                    return "K"
                case Card.Rank.ACE:
                    return "A"
                
        @classmethod
        def from_str(cls, rank_str):
            match (rank_str):
                case "2":
                    return Card.Rank.TWO
                case "3":
                    return Card.Rank.THREE
                case "4":
                    return Card.Rank.FOUR
                case "5":
                    return Card.Rank.FIVE
                case "6":
                    return Card.Rank.SIX
                case "7":
                    return Card.Rank.SEVEN
                case "8":
                    return Card.Rank.EIGHT
                case "9":
                    return Card.Rank.NINE
                case "10":
                    return Card.Rank.TEN
                case "Jack":
                    return Card.Rank.JACK
                case "Queen":
                    return Card.Rank.QUEEN
                case "King":
                    return Card.Rank.KING
                case "Ace":
                    return Card.Rank.ACE

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank
