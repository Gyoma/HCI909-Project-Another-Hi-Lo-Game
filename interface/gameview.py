import arcade
import arcade.gui

from game.gamemodel import GameModel
from common.card import Card
from interface.cardsprite import CardSprite
from interface.roundresultview import RoundResultView

from common import constants

from game import cardgame
from network.common.connection_command import ConnectionCommand

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.game = cardgame.game()

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

        ready_to_proceed_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="I'm ready",
        )

        @ready_to_proceed_button.event("on_click")
        def on_click_flatbutton(event):
            if (len(self.player_selected_cards_sprites) != constants.REQ_NUM_OF_CARDS_FOR_ROUND):
                return

            player_selected_cards = list(map(lambda card_sprite: card_sprite.card,
                                             self.player_selected_cards_sprites))
            
            args = [card.suit.name + '-' + card.rank.name for card in player_selected_cards]

            self.game.model.process_command(ConnectionCommand(ConnectionCommand.Command.COMPETE, args))

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(ready_to_proceed_button, anchor_x="right", anchor_y="top")

        self.__init_scroll_widgets()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        self.all_cards_sprites.draw()
        self.ui_manager.draw()

        # self.__draw_score()

    def on_update(self, delta_time: float):
        self.all_cards_sprites.move(self.move_cards_direction * delta_time * 500, 0)

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

        cards = arcade.get_sprites_at_point((x, y), self.player_available_cards_sprites)
        
        for card in cards:
            if (not card in self.player_selected_cards_sprites):
                if (len(self.player_selected_cards_sprites) == constants.REQ_NUM_OF_CARDS_FOR_ROUND):
                    return

                card.position = card.position[0], card.position[1] + 20
                self.player_selected_cards_sprites.append(card)
            else:
                card.position = card.position[0], card.position[1] - 20
                self.player_selected_cards_sprites.remove(card)

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

        for i, card_sprite in enumerate(self.all_cards_sprites):
            card_sprite.face_up()
            card_sprite.position = (i + 0.5) * card_width, card_height / 2
            if (card_sprite.card in self.game.model.player_available_cards):
                self.player_available_cards_sprites.append(card_sprite)
                continue

            card_sprite.alpha = 150

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
