from game.gamelogic import GameLogic
from cards.card import Card
from interface.cardsprite import CardSprite
from interface.gameresultview import GameResultView

from interface import gameview

import arcade
import arcade.gui

SELECTED_CARD_VERTICAL_INDENT = 300


class RoundResultView(arcade.View):
    def __init__(self, game, first_player_selected_cards, second_player_selected_cards, round_result):
        super().__init__()

        self.game = game
        self.round_result = round_result

        self.first_player_selected_cards_sprites = arcade.SpriteList()
        for card in first_player_selected_cards:
            self.first_player_selected_cards_sprites.append(CardSprite(card, is_face_up=True))

        self.second_player_selected_cards_sprites = arcade.SpriteList()
        for card in second_player_selected_cards:
            self.second_player_selected_cards_sprites.append(CardSprite(card, is_face_up=True))

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

    def setup(self):
        round_result_text = "It's a draw"
        match self.round_result:
            case GameLogic.Result.FIRST_PLAYER_WINS:
                round_result_text = "First player wins"
            case GameLogic.Result.SECOND_PLAYER_WINS:
                round_result_text = "Second player wins"
            case GameLogic.Result.DRAW:
                round_result_text = "It's a draw"

        round_result_label = arcade.gui.UILabel(
            font_size=32,
            align="center",
            text=round_result_text,
        )

        next_button = arcade.gui.UIFlatButton(
            center_x=300,
            center_y=100,
            width=200,
            height=40,
            text="Next",
        )

        @next_button.event("on_click")
        def on_click_flatbutton(event):
            if (self.game.state.rounds_left == 0):
                self.window.show_view(GameResultView(self.game.get_result()))
                self.window.current_view.setup()
                return

            self.window.show_view(gameview.GameView(self.game))
            self.window.current_view.setup()

        vertical_box = arcade.gui.UIBoxLayout()
        vertical_box.add(round_result_label)
        vertical_box.add(next_button)

        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=vertical_box,
        ))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        self.__draw_first_player_selected_cards()
        self.__draw_second_player_selected_cards()
        self.ui_manager.draw()

        self.__draw_score()

    def __draw_score(self):
        first_player_score_text = f"First player score: {self.game.get_first_player_win_rounds()}"
        arcade.draw_text(first_player_score_text, 10,
                         self.window.height - 20, arcade.color.WHITE, 14)
        second_player_score_text = f"Second player score: {self.game.get_second_player_win_rounds()}"
        arcade.draw_text(second_player_score_text, 10,
                         self.window.height - 40, arcade.color.WHITE, 14)
        rounds_left_text = f"Rounds left: {self.game.state.rounds_left}"
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

    def __draw_first_player_selected_cards(self):
        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(self.first_player_selected_cards_sprites, (
            self.window.height - card_height - SELECTED_CARD_VERTICAL_INDENT) / 2)

    def __draw_second_player_selected_cards(self):
        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(self.second_player_selected_cards_sprites, (
            self.window.height - card_height + SELECTED_CARD_VERTICAL_INDENT) / 2)