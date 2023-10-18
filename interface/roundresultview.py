import queue
from common import constants
from game import card_game
from interface.cardsprite import CardSprite
from interface.gameresultview import GameResultView

import game.settings as Settings

from interface import gameview

import arcade
import arcade.gui

from voice_recognition.voice_command_recognizer import VoiceCommand, VoiceVocabulary

SELECTED_CARD_VERTICAL_INDENT = 300

class RoundResultView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game = card_game.game()

        self.player_selected_cards_sprites = arcade.SpriteList()
        for card in self.game.model.player_selected_cards:
            self.player_selected_cards_sprites.append(CardSprite(card, is_face_up=True))

        self.opponent_selected_cards_sprites = arcade.SpriteList()
        for card in self.game.model.opponent_selected_cards:
            self.opponent_selected_cards_sprites.append(CardSprite(card, is_face_up=True))

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.go_to_next_round = False

        self.setup()

    def setup(self):
        round_result_text = "It's a draw"
        
        match self.game.model.round_result:
            case constants.RoundResult.WIN:
                round_result_text = "You win =)"
            case constants.RoundResult.LOSS:
                round_result_text = "You lose =("
            case constants.RoundResult.DRAW:
                round_result_text = "It's a draw"

        round_result_label = arcade.gui.UILabel(
            font_size=32,
            align="center",
            text=round_result_text,
        )

        next_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Next",
        )

        @next_button.event("on_click")
        def on_click_flatbutton(event):
            self.go_to_next_round = True

        vertical_box = arcade.gui.UIBoxLayout()
        vertical_box.add(round_result_label)
        vertical_box.add(next_button)

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(vertical_box,
                   anchor_x="center_x",
                   anchor_y="center_y")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.game.model.voice_recognizer.start()

        return super().on_show_view()

    def on_hide_view(self):
        self.game.model.voice_recognizer.stop()
        
        return super().on_hide_view()

    def on_draw(self):
        self.clear()

        self.__draw_player_selected_cards()
        self.__draw_opponent_selected_cards()
        self.ui_manager.draw()

        self.__draw_score()

    def on_update(self, delta_time: float):
        if (self.go_to_next_round):
            self.__next()
            self.go_to_next_round = False

        # Process voice commands
        voice_command_queue = self.game.model.voice_recognizer.command_queue
        
        while not voice_command_queue.empty():
            self.__process_voice_command(voice_command_queue.get())
            voice_command_queue.task_done()

        return super().on_update(delta_time)

    def __draw_score(self):
        first_player_score_text = f"Your score: {self.game.model.player_round_wins}"
        arcade.draw_text(first_player_score_text, 10,
                         self.window.height - 20, arcade.color.WHITE, 14)
        second_player_score_text = f"Opponent's score: {self.game.model.player_round_losses}"
        arcade.draw_text(second_player_score_text, 10,
                         self.window.height - 40, arcade.color.WHITE, 14)
        rounds_left_text = f"Rounds left: {self.game.model.rounds_left}"
        arcade.draw_text(rounds_left_text, 10,
                         self.window.height - 60, arcade.color.WHITE, 14)

    def __draw_cards_in_the_center(self, cards_sprites, y):
        card_width, card_height = CardSprite.card_sprite_size()
        horizontal_indent = 40
        num_selected_cards = len(cards_sprites)
        total_width = num_selected_cards * card_width + \
            horizontal_indent * (num_selected_cards - 1)
        start_x = (self.window.width - total_width) / 2
        for i, card_sprite in enumerate(cards_sprites):
            card_sprite.position = start_x + \
                (i * (card_width + horizontal_indent)) + \
                card_width / 2, card_height / 2 + y

        cards_sprites.draw()

    def __draw_player_selected_cards(self):
        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(self.player_selected_cards_sprites, (
            self.window.height - card_height - SELECTED_CARD_VERTICAL_INDENT) / 2)

    def __draw_opponent_selected_cards(self):
        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(self.opponent_selected_cards_sprites, (
            self.window.height - card_height + SELECTED_CARD_VERTICAL_INDENT) / 2)
        
    def __next(self):
        self.game.model.round_result = None
        self.game.model.player_selected_cards = []
        self.game.model.opponent_selected_cards = []

        self.window.show_view(gameview.GameView())
        # if (self.game.state.rounds_left == 0):
        #     self.window.show_view(GameResultView(self.game.get_result()))
        #     self.window.current_view.setup()
        #     return

        # self.window.show_view(gameview.GameView())
        # self.window.current_view.setup()

    def __process_voice_command(self, command : VoiceCommand):
        if command.name == VoiceVocabulary.NEXT.name.lower():
            self.go_to_next_round = True
