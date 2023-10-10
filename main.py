from interface.mainmenuview import MainMenuView

import arcade

def main():
    window = arcade.Window(1280, 720, resizable=True)
    window.show_view(MainMenuView())
    window.current_view.setup()
    arcade.run()

if __name__ == "__main__":
    main()