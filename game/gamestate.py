# from cards.card import Card

# import random
# import itertools


# class GameState():
#     def __init__(self, first_player_cards, second_player_cards, rounds_left, first_player_win_rounds, second_player_win_rounds):
#         self.first_player_cards = first_player_cards
#         self.second_player_cards = second_player_cards
#         self.rounds_left = rounds_left
#         self.first_player_win_rounds = first_player_win_rounds
#         self.second_player_win_rounds = second_player_win_rounds

#         self.first_player_available_cards = self.first_player_cards
#         self.second_player_available_cards = self.second_player_cards

#     @classmethod
#     def new_game(cls):
#         cards = []
#         card_parameters_combinations = itertools.product(Card.Suit, Card.Rank)
#         for suit, rank in card_parameters_combinations:
#             cards.append(Card(suit, rank))

#         first_player_cards = cards
#         second_player_cards = cards.copy()
#         rounds_left = 15
#         first_player_win_rounds = 0
#         second_player_win_rounds = 0

#         return GameState(first_player_cards, second_player_cards, rounds_left, first_player_win_rounds, second_player_win_rounds)
