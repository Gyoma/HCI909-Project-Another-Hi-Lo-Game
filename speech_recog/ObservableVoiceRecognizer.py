from utils.singletonmeta import SingletonMeta

import speech_recognition as sr
import weakref
import threading


class VoiceCommandObserver():
    def __init__(self, observer):
        self.observer = observer

    def update(self, command):
        self.observer(command)


class ObservableVoiceRecognizer(metaclass=SingletonMeta):
    def __init__(self, audio_src=0):
        self.observers = weakref.WeakSet()
        self.recognizer = sr.Recognizer()
        self.audio_src = audio_src
        self.stop_listening = self.recognizer.listen_in_background(
            sr.Microphone(device_index=self.audio_src), self.notify_observers, phrase_time_limit=2)

    def __del__(self):
        self.stop()

    def add_observer(self, observer):
        self.observers.add(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, recognizer, audio):
        text = self.__convert_voice_to_text(recognizer, audio)

        if text == "":
            return

        for observer in self.observers:
            observer.update(text)

    def set_parameters(self, audio_src):
        self.stop_listening(wait_for_stop=False)

        self.audio_src = audio_src
        self.stop_listening = self.recognizer.listen_in_background(
            sr.Microphone(device_index=self.audio_src), self.notify_observers, phrase_time_limit=2)

    def stop(self):
        self.stop_listening(wait_for_stop=False)

    def __convert_voice_to_text(self, recognizer, audio):
        try:
            text = recognizer.recognize_whisper(audio)
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError as e:
            text = ""
            print("Error; {0}".format(e))
        print(text)
        return text
