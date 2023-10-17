from interface import mainmenuview
from interface.settings import Settings

import arcade
import arcade.gui

import cv2

import speech_recognition as sr

import locale

class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.setup()

    def setup(self):
        cameras_list_label = arcade.gui.UILabel(
            font_size=18,
            align="center",
            text="Select camera:",
        )

        cameras_list = arcade.gui.UIDropdown(
            options=self.__list_available_cameras(),
            width=200,
            height=40,)
        
        @cameras_list.event("on_change")
        def on_change_dropdown(event):
            Settings().camera_id = int(event.new_value)

        microphones_list_label = arcade.gui.UILabel(
            font_size=18,
            align="center",
            text="Select microphone:",
        )

        microphones_list = arcade.gui.UIDropdown(
            options=self.__list_available_microphones(),
            width=200,
            height=40,)
        
        @microphones_list.event("on_change")
        def on_change_dropdown(event):
            Settings().microphone_id = self.__list_available_microphones().index(event.new_value)

        back_to_menu_button = arcade.gui.UIFlatButton(
            width=200,
            height=40,
            text="Back to main menu",
        )

        @back_to_menu_button.event("on_click")
        def on_click_flatbutton(event):
            self.window.show_view(mainmenuview.MainMenuView())
            self.window.current_view.setup()

        vertical_box = arcade.gui.UIBoxLayout()
        vertical_box.add(cameras_list_label)
        vertical_box.add(cameras_list)
        vertical_box.add(microphones_list_label)
        vertical_box.add(microphones_list)
        vertical_box.add(back_to_menu_button)

        layout = self.ui_manager.add(arcade.gui.UIAnchorLayout())

        layout.add(vertical_box, 
                   anchor_x="center_x",
                   anchor_y="center_y",)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()

        self.ui_manager.draw()

    def __list_available_cameras(self):
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(f"{i}")
                cap.release()
            else:
                break
        
        return available_cameras
    
    def __list_available_microphones(self):
        microphone_list = sr.Microphone.list_microphone_names()
        for i in range(len(microphone_list)):
            # Function 'list_microphone_names' return strings encoded in system preferred encoding.
            # Python's default encoding is utf-8, so we need to convert it to utf-8.
            microphone_list[i] = bytes(microphone_list[i], locale.getpreferredencoding()).decode("utf-8")
        return microphone_list
