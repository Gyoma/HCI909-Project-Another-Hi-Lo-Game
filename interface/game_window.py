import arcade
import cv2

from common import constants

class GameWindow(arcade.Window):
    """
    Main window class for the game.

    It passes the server messages to the model and shows the camera view independently from current interface view.
    """

    def __init__(self, game):
        super().__init__(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 
                         title="Another Hi-Lo Game", resizable=True)
        self.game = game
        self.set_min_size(constants.MIN_WINDOW_WIDTH, constants.MIN_WINDOW_HEIGHT)

    def on_update(self, delta_time: float):
        card_detector = self.game.model.card_detector

        # Open a new window to display the image from camera
        if card_detector is not None:
            image = card_detector.get_last_image()

            if (image is not None) and (image.ndim > 0):
                cv2.imshow('Camera View', image)

        # Process network commands
        read_queue = self.game.model.client.read_queue.sync_q
        while not read_queue.empty():
            self.game.model.process_client_command(read_queue.get())
            read_queue.task_done()

        cv2.waitKey(1)

        return super().on_update(delta_time)