from interface import gameview, settingsmenuview

import arcade
import arcade.gui

from interface.startsubmenu import StartSubMenu

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.setup()

    def setup(self):
        app_name_label = arcade.gui.UILabel(
            font_size=48,
            align="center",
            text="Another Hi-Lo Game",
        )

        new_game_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="New game",
        )

        @new_game_button.event("on_click")
        def on_click_flatbutton(event):
            self.ui_manager.add(StartSubMenu(), layer=1)

        settings_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Settings",
        )

        @settings_button.event("on_click")
        def on_click_flatbutton(event):
            self.window.show_view(settingsmenuview.SettingsView())
        
        quit_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Exit",
        )

        @quit_button.event("on_click")
        def on_click_flatbutton(event):
            arcade.exit()

        vertical_box = arcade.gui.UIBoxLayout(space_between=5)
        vertical_box.add(app_name_label)
        vertical_box.add(new_game_button)
        vertical_box.add(settings_button)
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
