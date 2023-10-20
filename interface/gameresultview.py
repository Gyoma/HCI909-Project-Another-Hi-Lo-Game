from game import card_game

import game.settings as Settings

from interface import gameview

import arcade
import arcade.gui
from game.settings import Settings
from voice_recognition.voice_command_recognizer import VoiceVocabulary

class GameResultView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game = card_game.game()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.play_new_game = False
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
            self.play_new_game = True
        
        quit_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Exit",
        )

        @quit_button.event("on_click")
        def on_click_flatbutton(event):
            self.quit = True

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
        # Process voice commands
        voice_command_queue = self.game.model.voice_recognizer.command_queue
        
        while not voice_command_queue.empty():
            self.__process_voice_command(voice_command_queue.get())
            voice_command_queue.task_done()

        if self.play_new_game:
            self.game.model.reset()
            self.window.show_view(gameview.GameView())
        elif self.quit:
            arcade.exit()

        return super().on_update(delta_time)
    
    def __process_voice_command(self, command):
        if command.name == VoiceVocabulary.PLAY.name.lower():
            if len(command.args) != command.nargs:
                return
            
            arg = command.args[0]

            if arg == VoiceVocabulary.AGAIN.name.lower():
                self.play_new_game = True
                return
            
        if command.name == VoiceVocabulary.EXIT.name.lower():
            self.quit = True
