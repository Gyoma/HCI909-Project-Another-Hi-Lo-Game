import arcade
import cv2

from common import constants

class GameWindow(arcade.Window):
    def __init__(self, game):
        super().__init__(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 
                         title="Another Hi-Lo Game", resizable=True)
        self.game = game
        self.set_min_size(constants.MIN_WINDOW_WIDTH, constants.MIN_WINDOW_HEIGHT)

    def on_update(self, delta_time: float):
        # cv2.namedWindow('Camera View')

        card_detector = self.game.model.card_detector.card_detector

        if card_detector is not None:
            image, _ = card_detector.last_images()

            if image is not None:
                cv2.imshow('Camera View', image)

        # Process network commands
        read_queue = self.game.model.client.read_queue.sync_q
        while not read_queue.empty():
            self.game.model.process_client_command(read_queue.get())
            read_queue.task_done()

        cv2.waitKey(1)

        return super().on_update(delta_time)