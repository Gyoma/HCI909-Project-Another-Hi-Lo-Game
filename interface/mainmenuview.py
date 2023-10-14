from interface import gameview

import arcade

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

    def setup(self):
        app_name_label = arcade.gui.UILabel(
            font_size=72,
            align="center",
            text="Attack game",
        )

        new_game_button = arcade.gui.UIFlatButton(
            center_x=300,
            center_y=100,
            width=200,
            height=40,
            text="New game",
        )

        @new_game_button.event("on_click")
        def on_click_flatbutton(event):
            self.window.show_view(gameview.GameView(gameview.GameLogic()))
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
        vertical_box.add(app_name_label)
        vertical_box.add(new_game_button)
        vertical_box.add(quit_button)

        self.ui_manager.add(arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=vertical_box,
        ))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        self.ui_manager.draw()