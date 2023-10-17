from utils.singletonmeta import SingletonMeta

class Settings(metaclass=SingletonMeta):
    def __init__(self):
        self.camera_id = 0
        self.microphone_id = 0
