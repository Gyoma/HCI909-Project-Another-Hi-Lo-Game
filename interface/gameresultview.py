from game import card_game

import game.settings as Settings

from interface import gameview

import arcade
import arcade.gui
from game.settings import Settings

class GameResultView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game = card_game.game()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.go_to_next_game = False
        self.quit = False

        self.setup()

    def setup(self):
        game_result_text = "It's a draw"

        if self.game.model.player_round_wins > self.game.model.player_round_losses:
            game_result_text = 'You win this game =)'
        elif self.game.model.player_round_wins < self.game.model.player_round_losses:
            game_result_text = 'You lose this game =('

        game_result_label = arcade.gui.UILabel(
            font_size=32,
            align="center",
            text=game_result_text,
        )

        play_again_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Play again",
        )

        @play_again_button.event("on_click")
        def on_click_flatbutton(event):
            self.game.model.reset()
            self.window.show_view(gameview.GameView())
        
        quit_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Quit",
        )

        @quit_button.event("on_click")
        def on_click_flatbutton(event):
            arcade.exit()

        vertical_box = arcade.gui.UIBoxLayout(space_between=5)
        vertical_box.add(game_result_label)
        vertical_box.add(play_again_button)
        vertical_box.add(quit_button)

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(vertical_box,
                   anchor_x="center_x",
                   anchor_y="center_y",)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.game.model.voice_recognizer.start()

        return super().on_show_view()

    def on_hide_view(self):
        self.game.model.voice_recognizer.stop()

        return super().on_hide_view()

    def on_draw(self):
        self.clear()

        self.ui_manager.draw()

    def on_update(self, delta_time: float):
        return super().on_update(delta_time)
