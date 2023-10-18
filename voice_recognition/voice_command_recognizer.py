import speech_recognition as sr
from enum import Enum

import queue
import copy

class VoiceVocabulary(Enum):
    LOAD = 0,
    READY = 0,
    NEXT = 1,
    SWITCH = 2,
    LEFT = 3,
    MIDDLE = 4,
    RIGHT = 5

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

        self.vocabulary = [
            VoiceCommand(VoiceVocabulary.LOAD.name.lower(), 0),
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

        self.stop_listening = self.recognizer.listen_in_background(
            sr.Microphone(device_index=self.audio_src), 
            callback=self.__process_phrase, 
            phrase_time_limit=5)

    def stop(self):
        if self.stop_listening == None:
            return
        
        self.stop_listening(wait_for_stop=False)
        self.stop_listening = None

    def __process_phrase(self, recognizer, audio):
        text = self.__convert_voice_to_text(audio)

        print(text)

        if not text:
            return
        
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
