import os
from enum import Enum

class ConnectionCommand:
    class Command(Enum):
        COMPETE = 0
        USED_CARDS = 1
        RESULT = 2
        STATUS = 3
    
    def __init__(self, command : Command, args : list[str]):
        self._command = command
        self._args = args

    def command(self):
        return self._command
    
    def name(self):
        return self._command.name
    
    def args(self):
        return self._args
    
    def pack(self):
        return (' '.join([self._command.name, ' '.join(self._args)]) + os.linesep).encode('utf8')