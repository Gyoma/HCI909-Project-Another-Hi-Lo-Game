from enum import Enum

# UI constants

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 360

class RoundResult(Enum):
    DRAW = 0
    WIN = 1
    LOSS = 2

# Server-Client constants

DISCONNECT_TIMEOUT_SEC = 120
SERVER_PORT = 3306

# Card detector constants

CARD_WIDTH=320
CARD_HEIGHT=448

CARD_CORNER_WIDTH=128
CARD_CORNER_HEIGHT=128

REQ_CARDS_NUM = 3

# Common constants

REQ_NUM_OF_PLAYERS = 2
REQ_NUM_OF_CARDS_FOR_ROUND = 3
MAX_NUM_OF_ROUNDS = 15

CARD_NAMES = ['H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK', 'HA', 
              'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'SJ', 'SQ', 'SK', 'SA',  
              'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK', 'CA', 
              'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'DJ', 'DQ', 'DK', 'DA']

CAPITALIZED_SUITS = {
    'Spades' : 'SPADES',
    'Clubs' : 'CLUBS',
    'Hearts' : 'HEARTS',
    'Diamonds' : 'DIAMONDS'
}

CAPITALIZED_RANKS = {
    '2' : 'TWO',
    '3' : 'THREE',
    '4' : 'FOUR',
    '5' : 'FIVE',
    '6' : 'SIX',
    '7' : 'SEVEN',
    '8' : 'EIGHT',
    '9' : 'NINE',
    '10' : 'TEN',
    'Jack' : 'JACK',
    'Queen' : 'QUEEN',
    'King' : 'KING',
    'Ace' : 'ACE'
}

SHORT_RANKS = {
    'TWO' : '2',
    'THREE' : '3',
    'FOUR' : '4',
    'FIVE' : '5',
    'SIX' : '6',
    'SEVEN' : '7',
    'EIGHT' : '8',
    'NINE' : '9',
    'TEN' : '10',
    'JACK' : 'J',
    'QUEEN' : 'Q',
    'KING' : 'K',
    'ACE' : 'A'
}

FULL_RANKS = {
    '2' : 'TWO',
    '3' : 'THREE',
    '4' : 'FOUR',
    '5' : 'FIVE',
    '6' : 'SIX',
    '7' : 'SEVEN',
    '8' : 'EIGHT',
    '9' : 'NINE',
    '10' : 'TEN',
    'J' : 'JACK',
    'Q' : 'QUEEN',
    'K' : 'KING',
    'A' : 'ACE'
}

SHORT_SUITS = {
    'SPADES' : 'S',
    'CLUBS' : 'C',
    'HEARTS' : 'H',
    'DIAMONDS' : 'D'
}

FULL_SUITS = {
    'S' : 'SPADES',
    'C' : 'CLUBS',
    'H' : 'HEARTS',
    'D' : 'DIAMONDS'
}

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

DEBUG_SESSION = True