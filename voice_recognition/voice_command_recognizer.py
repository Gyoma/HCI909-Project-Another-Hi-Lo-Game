import speech_recognition as sr
from enum import Enum

import queue
import copy
import threading

from common import constants
from game import card_game

class VoiceVocabulary(Enum):
    START = 0,
    READY = 1,
    NEXT = 2,
    SWITCH = 3,
    LEFT = 4,
    MIDDLE = 5,
    RIGHT = 6

class VoiceCommand:
    def __init__(self, name = None, nargs = 0, args = [], variants = [], different = True):
        self.name = name
        self.nargs = nargs
        self.variants = variants
        self.different = different
        self.args = args

class VoiceCommandRecognizer:

    def __init__(self, audio_src = 0, max_queue_size = 3):
        self.recognizer = sr.Recognizer()
        self.audio_src = audio_src
        self.max_queue_size = max_queue_size
        self.stop_listening = None
        self.thread = None
        self.listening = False

        self.vocabulary = [
            VoiceCommand(VoiceVocabulary.START.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.READY.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.NEXT.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.SWITCH.name.lower(), nargs=2, variants=[
                VoiceVocabulary.LEFT.name.lower(), 
                VoiceVocabulary.MIDDLE.name.lower(),
                VoiceVocabulary.RIGHT.name.lower()])
        ]
        
        self.command_queue = queue.Queue()

    def __del__(self):
        self.stop()

    def start(self):
        self.stop()

        self.listening = True
        self.thread = threading.Thread(target=self.__run, daemon=True)
        self.thread.start()

    def stop(self):
        self.listening = False
        
        if self.thread is not None:
            self.thread.join()

        self.thread = None

    def __run(self):

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

            while self.listening:
                try:  # listen for 1 second, then check again if the stop function has been called
                    audio = self.recognizer.listen(source, phrase_time_limit=5)
                    self.__process_phrase(audio)
                except sr.WaitTimeoutError:  # listening timed out, just try again
                    pass

            # self.stop_listening = self.recognizer.listen_in_background(
            #     source, #device_index=self.audio_src), 
            #     callback=self.__process_phrase, 
            #     phrase_time_limit=5)


    def __process_phrase(self, audio):
        # print(audio)

        text = self.__convert_voice_to_text(audio)

        if not text:
            return
        
        if constants.DEBUG_SESSION:
            print(f'You said: {text}')
        
        recognized_command = None

        # Only one command per a phrase
        for command in self.vocabulary:
            index = text.find(command.name)
            
            if index != -1:
                text = text[index + len(command.name):]
                recognized_command = copy.deepcopy(command)

                for variant in recognized_command.variants:
                    index = text.find(variant)

                    if index != -1:
                        text = text[index + len(variant):]
                        recognized_command.args.append(variant)

                    if len(recognized_command.args) == recognized_command.nargs:
                        break

                break

        if (recognized_command is not None) and (len(recognized_command.args) == recognized_command.nargs):
            while self.command_queue.qsize() >= self.max_queue_size:
                task = self.command_queue.get()
                self.command_queue.task_done()

            self.command_queue.put(recognized_command)

    def __convert_voice_to_text(self, audio):
        try:
            text = self.recognizer.recognize_whisper(audio, model='base.en', language="english")
        except sr.UnknownValueError:
            text = ""

        # print(text)
        return text.lower()
    
# def is_command(text, required_command):
#     return text.lower().count(required_command.lower()) > 0
