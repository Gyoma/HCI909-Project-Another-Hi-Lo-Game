from game.gamelogic import GameLogic
from cards.card import Card
from interface.cardsprite import CardSprite
from interface.roundresultview import RoundResultView
from interface.settings import Settings
from detector.ObservableCardDetector import ObservableCardDetector
from speech_recog.ObservableVoiceRecognizer import ObservableVoiceRecognizer, VoiceCommandObserver

import arcade
import arcade.gui
import random
import threading
import time


class CardsChangeObserver():
    def __init__(self, observer):
        self.observer = observer

    def update(self, cards):
        self.observer(cards)


class GameView(arcade.View):
    def __init__(self, game):
        super().__init__()

        self.first_player_selected_cards = []

        self.game = game

        self.all_cards_sprites = arcade.SpriteList()
        for card in GameLogic.get_all_cards():
            self.all_cards_sprites.append(CardSprite(card))

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.move_cards = False
        self.move_task = None

        self.card_observer = CardsChangeObserver(
            lambda cards: self.__select_cards(cards))

        self.voice_command_observer = VoiceCommandObserver(
            lambda command: self.__handle_voice_command(command))
        
        self.player_ready = False

    def __del__(self):
        ObservableCardDetector(
            Settings().camera_id).remove_observer(self.card_observer)

    def setup(self):
        self.__update_first_player_cards()

        ready_to_proceed_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="I'm ready",
        )

        @ready_to_proceed_button.event("on_click")
        def on_click_flatbutton(event):
            self.__proseed_round()

        score_label = arcade.gui.UILabel(
            font_size=18,
            width=300,
            align="left",
            multiline=True,
            text=f"First player score: {self.game.get_first_player_win_rounds()}\n"
            f"Second player score: {self.game.get_second_player_win_rounds()}\n"
            f"Rounds left: {self.game.state.rounds_left}",
        )

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(ready_to_proceed_button, anchor_x="right", anchor_y="top")

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(score_label, anchor_x="left", anchor_y="top")

        self.__init_scroll_widgets()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)
        ObservableCardDetector(
            Settings().camera_id).add_observer(self.card_observer)
        ObservableVoiceRecognizer(
            Settings().microphone_id).add_observer(self.voice_command_observer)
        self.__select_cards(ObservableCardDetector(
            Settings().camera_id).get_cards())

    def on_hide_view(self):
        ObservableCardDetector(
            Settings().camera_id).remove_observer(self.card_observer)
        ObservableVoiceRecognizer(
            Settings().microphone_id).remove_observer(self.voice_command_observer)
        return super().on_hide_view()

    def on_draw(self):
        self.clear()

        self.all_cards_sprites.draw()
        self.ui_manager.draw()

        self.__draw_first_player_selected_cards()

    def on_mouse_press(self, x, y, button, modifiers):
        if (self.scroll_left_button.center_x - self.scroll_left_button.width / 2 <= x <= self.scroll_left_button.center_x + self.scroll_left_button.width / 2 and
                self.scroll_left_button.center_y - self.scroll_left_button.height / 2 <= y <= self.scroll_left_button.center_y + self.scroll_left_button.height / 2):
            self.move_cards = True
            self.move_task = threading.Thread(target=self.__move_cards_left)
            self.move_task.start()
            return

        if (self.scroll_right_button.center_x - self.scroll_right_button.width / 2 <= x <= self.scroll_right_button.center_x + self.scroll_right_button.width / 2 and
                self.scroll_right_button.center_y - self.scroll_right_button.height / 2 <= y <= self.scroll_right_button.center_y + self.scroll_right_button.height / 2):
            self.move_cards = True
            self.move_task = threading.Thread(target=self.__move_cards_right)
            self.move_task.start()
            return

    def on_mouse_release(self, x, y, button, modifiers):
        self.move_cards = False

    def on_update(self, delta_time: float):
        if self.player_ready:
            self.__proseed_round()
            self.player_ready = False

        return super().on_update(delta_time)

    def __init_scroll_widgets(self):
        self.scroll_left_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Left",
        )

        layout1 = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout1.add(self.scroll_left_button,
                    anchor_x="left",
                    anchor_y="bottom",)

        self.scroll_right_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Right",
        )

        layout2 = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout2.add(self.scroll_right_button,
                    anchor_x="right",
                    anchor_y="bottom",)

    def __move_cards_left(self):
        while (self.move_cards):
            self.all_cards_sprites.move(5, 0)
            time.sleep(0.01)

    def __move_cards_right(self):
        while (self.move_cards):
            self.all_cards_sprites.move(-5, 0)
            time.sleep(0.01)

    def __update_first_player_cards(self):
        card_width, card_height = CardSprite.card_sprite_size()

        for i, card_sprite in enumerate(self.all_cards_sprites):
            card_sprite.face_up()
            card_sprite.position = (i + 0.5) * card_width, card_height / 2
            if (card_sprite.card in self.game.get_first_player_available_cards()):
                continue

            card_sprite.alpha = 150

    def __select_cards(self, cards):
        self.first_player_selected_cards = []

        for card in cards:
            if (len(self.first_player_selected_cards) >= GameLogic.CARDS_USED_PER_ROUND):
                break

            if (card in self.first_player_selected_cards):
                continue

            if (not card in self.game.get_first_player_available_cards()):
                continue

            self.first_player_selected_cards.append(card)

    def __proseed_round(self):
        first_player_selected_cards = self.first_player_selected_cards.copy()

        if (len(first_player_selected_cards) != GameLogic.CARDS_USED_PER_ROUND):
            return

        second_player_selected_cards = random.sample(
            self.game.get_second_player_available_cards(), GameLogic.CARDS_USED_PER_ROUND)

        round_result = self.game.proceed_round(
            first_player_selected_cards, second_player_selected_cards)

        self.__update_first_player_cards()

        self.window.show_view(RoundResultView(
            self.game, first_player_selected_cards, second_player_selected_cards, round_result))
        self.window.current_view.setup()

    def __handle_voice_command(self, command):
        lower_command = command.lower()
        if (lower_command.count("ready") > 0 or
            lower_command.count("compete") > 0 or
            lower_command.count("proceed") > 0 or
                lower_command.count("attack") > 0):
            self.player_ready = True

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
        first_player_selected_cards_sprites = arcade.SpriteList()
        for card in self.first_player_selected_cards:
            first_player_selected_cards_sprites.append(
                CardSprite(card, is_face_up=True))

        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(first_player_selected_cards_sprites, (
            self.window.height - card_height) / 2)
