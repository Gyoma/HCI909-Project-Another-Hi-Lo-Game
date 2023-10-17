import arcade
import arcade.gui
from game import card_game

from common import constants
from interface.gameview import GameView

DARK_AMAZON = arcade.types.Color(35, 73, 52)


class StartSubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    """Acts like a fake view/window."""

    # , title: str, input_text: str, toggle_label: str, dropdown_options: List[str], slider_label: str):
    def __init__(self):
        super().__init__(size_hint=(1, 1))

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(
            width=constants.MIN_WINDOW_WIDTH, 
            height=constants.MIN_WINDOW_HEIGHT, 
            size_hint=None))
        frame.with_padding(all=20)

        # Add a background to the window.
        # Nine patch smoothes the edges.
        frame.with_background(color=DARK_AMAZON)
        frame.with_border(color=arcade.color.GRAY)

        title_label = arcade.gui.UILabel(
            text="Let's go!",
            width=200, 
            align="center",
            font_size=20)
        
        # Adding some extra space around the title.
        extra_space = arcade.gui.UISpace(height=30, color=DARK_AMAZON)

        create_session_button = arcade.gui.UIFlatButton(text="Create session",
                                                        width=200,
                                                        height=40)

        host_label = arcade.gui.UILabel(text="Enter host", width=200, align="center", font_size=20)
        
        host_text_widget = arcade.gui.UIInputText(width=200, 
                                                  height=40, 
                                                  font_size=14,
                                                  text_color=arcade.color.WHITE).with_border(color=arcade.color.GRAY)

        connect_button = arcade.gui.UIFlatButton(text="Connect",
                                                 width=200,
                                                 height=40)

        back_button = arcade.gui.UIFlatButton(text="Back",
                                              width=200,
                                              height=40)
        

        @create_session_button.event("on_click")
        def on_click_back_button(event):
            game = card_game.game()
            
            game.model.start_server()
            game.model.connect()

            arcade.get_window().show_view(GameView())
            self.parent.remove(self)

        @connect_button.event("on_click")
        def on_click_back_button(event):
            game = card_game.game()
            game.model.connect(host_text_widget.text)            

            arcade.get_window().show_view(GameView())
            self.parent.remove(self)

        @back_button.event("on_click")
        def on_click_back_button(event):
            self.parent.remove(self)

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=5)

        widget_layout.add(title_label)
        widget_layout.add(extra_space)
        widget_layout.add(create_session_button)
        widget_layout.add(host_label)
        widget_layout.add(host_text_widget)
        widget_layout.add(connect_button)
        widget_layout.add(extra_space)
        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")
