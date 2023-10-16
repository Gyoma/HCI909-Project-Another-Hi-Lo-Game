from cards.card import Card
from enum import Enum

import itertools

class GameModel():
    CARDS_USED_PER_ROUND = 3

    class Result(Enum):
        DRAW = 0
        FIRST_PLAYER_WINS = 1
        SECOND_PLAYER_WINS = 2

    def __init__(self):
        self.player_available_cards = self.get_all_cards()
        self.player_used_cards = []
        self.player_selected_cards = []
        self.opponent_selected_cards = []

    @classmethod
    def get_all_cards(cls):
        return [Card(suit, rank) for suit, rank in itertools.product(Card.Suit, Card.Rank)]
    
    # def 

    # def get_first_player_available_cards(self):
    #     return self.state.first_player_available_cards
    
    # def get_second_player_available_cards(self):
    #     return self.state.second_player_available_cards
    
    # def get_first_player_win_rounds(self):
    #     return self.state.first_player_win_rounds
    
    # def get_second_player_win_rounds(self):
    #     return self.state.second_player_win_rounds
    
    # def get_result(self):
    #     if (self.state.rounds_left != 0):
    #         raise RuntimeError("There are more rounds to proceed")
        
    #     if (self.state.first_player_win_rounds > self.state.second_player_win_rounds):
    #         return GameModel.Result.FIRST_PLAYER_WINS
    #     elif (self.state.first_player_win_rounds < self.state.second_player_win_rounds):
    #         return GameModel.Result.SECOND_PLAYER_WINS
    #     else:
    #         return GameModel.Result.DRAW

    # def proceed_round(self, first_player_selected_cards, second_player_selected_cards):
    #     if (self.state.rounds_left == 0):
    #         raise RuntimeError("There are no more rounds to proceed")

    #     if (len(first_player_selected_cards) != GameModel.CARDS_USED_PER_ROUND or
    #         len(second_player_selected_cards) != GameModel.CARDS_USED_PER_ROUND):
    #         raise RuntimeError("Each player must use exactly {} cards to proceed round".format(GameModel.CARDS_USED_PER_ROUND))
        
    #     first_player_rest_cards = self.state.first_player_cards
    #     for card in first_player_selected_cards:
    #         first_player_rest_cards.remove(card)

    #     second_player_rest_cards = self.state.second_player_cards
    #     for card in second_player_selected_cards:
    #         second_player_rest_cards.remove(card)

    #     first_player_selected_sorted_cards = sorted(first_player_selected_cards, key=lambda card: card.rank.value, reverse=True)
    #     second_player_selected_sorted_cards = sorted(second_player_selected_cards, key=lambda card: card.rank.value, reverse=True)

    #     first_player_beats_count = 0
    #     second_player_beats_count = 0

    #     while (len(first_player_selected_sorted_cards) > 0 and len(second_player_selected_sorted_cards) > 0):
    #         if (first_player_selected_sorted_cards[0].rank.value > second_player_selected_sorted_cards[0].rank.value):
    #             for card in second_player_selected_sorted_cards:
    #                 if (card.suit != first_player_selected_sorted_cards[0].suit):
    #                     continue

    #                 first_player_beats_count += 1
    #                 second_player_selected_sorted_cards.remove(card)
    #                 break

    #             first_player_selected_sorted_cards.remove(first_player_selected_sorted_cards[0])

    #         else:
    #             for card in first_player_selected_sorted_cards:
    #                 if (card.suit != second_player_selected_sorted_cards[0].suit):
    #                     continue

    #                 second_player_beats_count += 1
    #                 first_player_selected_sorted_cards.remove(card)
    #                 break

    #             second_player_selected_sorted_cards.remove(second_player_selected_sorted_cards[0])

    #     if (first_player_beats_count > second_player_beats_count):
    #         self.state.first_player_win_rounds += 1
        
    #     if (first_player_beats_count < second_player_beats_count):
    #         self.state.second_player_win_rounds += 1

    #     self.state = GameState(first_player_rest_cards,
    #                            second_player_rest_cards,
    #                            self.state.rounds_left - 1,
    #                            self.state.first_player_win_rounds,
    #                            self.state.second_player_win_rounds)
        
    #     if (first_player_beats_count > second_player_beats_count):
    #         return GameModel.Result.FIRST_PLAYER_WINS
        
    #     if (first_player_beats_count < second_player_beats_count):
    #         return GameModel.Result.SECOND_PLAYER_WINS

    #     return GameModel.Result.DRAW
