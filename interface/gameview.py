import arcade
import arcade.gui

from game.game_model import GameModel
from common.card import Card
from interface.cardsprite import CardSprite
from interface.gameresultview import GameResultView
from interface.roundresultview import RoundResultView

from game import card_game

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game = card_game.game()

        self.player_selected_cards_sprites = arcade.SpriteList()
        self.player_available_cards_sprites = arcade.SpriteList()

        self.all_cards_sprites = arcade.SpriteList()
        for card in GameModel.get_all_cards():
            self.all_cards_sprites.append(CardSprite(card))

        self.opponent_selected_cards_sprites = arcade.SpriteList()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.move_cards_direction = 0

        self.setup()

    def setup(self):
        self.__update_player_cards()

        # ready_to_proceed_button = arcade.gui.UIFlatButton(
        #     width=200,
        #     height=40,
        #     text="I'm ready",
        # )

        # @ready_to_proceed_button.event("on_click")
        # def on_click_flatbutton(event):
        #     if (len(self.player_selected_cards_sprites) != constants.REQ_NUM_OF_CARDS_FOR_ROUND):
        #         return

        #     player_selected_cards = list(map(lambda card_sprite: card_sprite.card,
        #                                      self.player_selected_cards_sprites))

        #     args = [card.suit.name + '-' +
        #             card.rank.name for card in player_selected_cards]

        #     self.game.model.process_command(ConnectionCommand(
        #         ConnectionCommand.Command.COMPETE, args))

            # self.__proseed_round()

        self.score_label = arcade.gui.UILabel(
            font_size=18,
            width=300,
            align="left",
            multiline=True,
            text=f"Your score: {self.game.model.player_round_wins}\n"
            f"Opponent's score: {self.game.model.player_round_losses}\n"
            f"Rounds left: {self.game.model.rounds_left}",
        )

        # layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())
        # layout.add(ready_to_proceed_button, anchor_x="right", anchor_y="top")

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())
        layout.add(self.score_label, anchor_x="left", anchor_y="top")

        self.__init_scroll_widgets()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.game.model.card_detector.start()

    def on_hide_view(self):
        self.game.model.card_detector.stop()

        return super().on_hide_view()

    def on_draw(self):
        self.clear()

        self.player_available_cards_sprites.draw()
        self.ui_manager.draw()

        self.__draw_player_selected_cards()

    def on_update(self, delta_time: float):
        self.player_available_cards_sprites.move(self.move_cards_direction * delta_time * 500, 0)
        self.game.model.player_selected_cards = self.game.model.card_detector.get_cards()

        if self.game.model.round_result is not None:
            if self.game.model.rounds_left == 0:
                self.window.show_view(GameResultView())
            else:
                self.window.show_view(RoundResultView())

            self.__update_player_cards()

        # Update score label
        self.score_label.text = f"Your score: {self.game.model.player_round_wins}\n"
        f"Opponent's score: {self.game.model.player_round_losses}\n"
        f"Rounds left: {self.game.model.rounds_left}"

        return super().on_update(delta_time)

    def on_mouse_press(self, x, y, button, modifiers):
        if (self.scroll_left_button.center_x - self.scroll_left_button.width / 2 <= x <= self.scroll_left_button.center_x + self.scroll_left_button.width / 2 and
                self.scroll_left_button.center_y - self.scroll_left_button.height / 2 <= y <= self.scroll_left_button.center_y + self.scroll_left_button.height / 2):
            self.move_cards_direction = 1.
            return

        if (self.scroll_right_button.center_x - self.scroll_right_button.width / 2 <= x <= self.scroll_right_button.center_x + self.scroll_right_button.width / 2 and
                self.scroll_right_button.center_y - self.scroll_right_button.height / 2 <= y <= self.scroll_right_button.center_y + self.scroll_right_button.height / 2):
            self.move_cards_direction = -1.
            return

    def on_mouse_release(self, x, y, button, modifiers):
        self.move_cards_direction = 0.

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

    def __update_player_cards(self):
        card_width, card_height = CardSprite.card_sprite_size()

        self.player_selected_cards_sprites.clear()
        self.player_available_cards_sprites.clear()

        i = 0
        for card_sprite in self.all_cards_sprites:
            card_sprite.face_up()

            if (card_sprite.card in self.game.model.player_available_cards):
                card_sprite.position = (i + 0.5) * card_width, card_height / 2
                self.player_available_cards_sprites.append(card_sprite)
                i += 1
                continue

            card_sprite.alpha = 150

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
        player_selected_cards_sprites = arcade.SpriteList()
        for card in self.game.model.player_selected_cards:
            player_selected_cards_sprites.append(
                CardSprite(card, is_face_up=True))

        _, card_height = CardSprite.card_sprite_size()
        self.__draw_cards_in_the_center(player_selected_cards_sprites, (
            self.window.height - card_height) / 2)
