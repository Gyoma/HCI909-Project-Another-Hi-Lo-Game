from game.gamelogic import GameLogic
from cards.card import Card
from interface.cardsprite import CardSprite

from interface import gameview

import arcade
import arcade.gui

SELECTED_CARD_VERTICAL_INDENT = 300


class GameResultView(arcade.View):
    def __init__(self, game_result):
        super().__init__()

        self.game_result = game_result

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

    def setup(self):
        game_result_text = "It's a draw"
        match self.game_result:
            case GameLogic.Result.FIRST_PLAYER_WINS:
                game_result_text = "First player wins"
            case GameLogic.Result.SECOND_PLAYER_WINS:
                game_result_text = "Second player wins"
            case GameLogic.Result.DRAW:
                game_result_text = "It's a draw"

        game_result_label = arcade.gui.UILabel(
            font_size=32,
            align="center",
            text=game_result_text,
        )

        play_again_button = arcade.gui.UIFlatButton(
            center_x=300,
            center_y=100,
            width=200,
            height=40,
            text="Play again",
        )

        @play_again_button.event("on_click")
        def on_click_flatbutton(event):
            self.window.show_view(gameview.GameView(GameLogic()))
            self.window.current_view.setup()
        
        quit_button = arcade.gui.UIFlatButton(
            center_x=300,
            center_y=50,
            width=200,
            height=40,
            text="Quit",
        )

        @quit_button.event("on_click")
        def on_click_flatbutton(event):
            arcade.exit()

        vertical_box = arcade.gui.UIBoxLayout()
        vertical_box.add(game_result_label)
        vertical_box.add(play_again_button)
        vertical_box.add(quit_button)

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(vertical_box,
                   anchor_x="center_x",
                   anchor_y="center_y",)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        self.ui_manager.draw()
