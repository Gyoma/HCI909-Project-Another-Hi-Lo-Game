_settings = None

def settings_instance():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

class Settings():
    def __init__(self):
        self.camera_id = 0
        self.microphone_id = 0
