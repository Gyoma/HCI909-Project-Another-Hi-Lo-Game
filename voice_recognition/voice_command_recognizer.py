import speech_recognition as sr
from enum import Enum

import queue
import copy
import threading

from common import constants

class VoiceVocabulary(Enum):
    """
    List of (sub-)commands available to use
    """
        
    START = 0,
    READY = 1,
    NEXT = 2,
    SWITCH = 3,
    LEFT = 4,
    MIDDLE = 5,
    RIGHT = 6,
    PLAY = 7,
    AGAIN = 8,
    EXIT = 9

class VoiceCommand:
    """
    Class representing a voice command
    """
        
    def __init__(self, name = None, nargs = 0, args = [], variants = [], different = True):
        """
        name - Name of a command. See VoiceVocabulary\n
        nargs - Number of required arguments\n
        args - List of arguments\n
        variants - Set of all possible arguments\n
        different - Flag showing whether all arguments must be different
        """
        self.name = name
        self.nargs = nargs
        self.variants = variants
        self.different = different
        self.args = args

class VoiceCommandRecognizer:
    """
    A class for the voice recognition. It runs in its' own thread as daemon.\n
    The last max_queue_size processed commands can be obtained with command_queue property
    """

    def __init__(self, audio_src = 0, max_queue_size = 3):
        self.recognizer = sr.Recognizer()
        self.audio_src = audio_src
        self.max_queue_size = max_queue_size
        self.stop_listening = None
        self.thread = None
        self.listening = False

        self.commands = [
            VoiceCommand(VoiceVocabulary.START.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.READY.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.NEXT.name.lower(), 0),
            VoiceCommand(VoiceVocabulary.SWITCH.name.lower(), nargs=2, variants=[
                VoiceVocabulary.LEFT.name.lower(), 
                VoiceVocabulary.MIDDLE.name.lower(),
                VoiceVocabulary.RIGHT.name.lower()]),
            VoiceCommand(VoiceVocabulary.PLAY.name.lower(), nargs=1, variants=[
                VoiceVocabulary.AGAIN.name.lower()]),
            VoiceCommand(VoiceVocabulary.EXIT.name.lower(), 0),
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
                try:  
                    # listen for 5 second
                    audio = self.recognizer.listen(source, phrase_time_limit=5)
                    self.__process_phrase(audio)
                except sr.WaitTimeoutError:  
                    # listening timed out, just try again
                    pass

    def __process_phrase(self, audio):
        text = self.__convert_audio_to_text(audio)

        if not text:
            return
        
        if constants.DEBUG_SESSION:
            print(f'You said: {text}')
        
        recognized_command = None

        # Only one command per a phrase is allowed.
        # So, we are going to find it and create (if any) an appropriate voice command
        for command in self.commands:
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

    def __convert_audio_to_text(self, audio):
        try:
            text = self.recognizer.recognize_whisper(audio, model='base.en', language="english")
        except sr.UnknownValueError:
            text = ''

        return text.lower()
