from interface.mainmenuview import MainMenuView

import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 360

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, title="Another Hi-Lo Game", resizable=True)
    window.set_min_size(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    window.show_view(MainMenuView())
    arcade.run()

if __name__ == "__main__":
    main()