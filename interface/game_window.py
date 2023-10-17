import arcade

from common import constants

class GameWindow(arcade.Window):
    def __init__(self, game):
        super().__init__(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, 
                         title="Another Hi-Lo Game", resizable=True)
        self.game = game
        self.set_min_size(constants.MIN_WINDOW_WIDTH, constants.MIN_WINDOW_HEIGHT)

    def on_update(self, delta_time: float):

        # Process network commands
        read_queue = self.game.model.client.read_queue.sync_q
        while not read_queue.empty():
            self.game.model.process_client_command(read_queue.get())
            read_queue.task_done()

        # Process voice commands
        voice_command_queue = self.game.model.voice_recognizer.command_queue
        while not voice_command_queue.empty():
            self.game.model.process_voice_command(voice_command_queue.get())
            voice_command_queue.task_done()

        return super().on_update(delta_time)