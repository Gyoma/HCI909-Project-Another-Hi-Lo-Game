import os
from enum import Enum

class ConnectionCommand:
    class Command(Enum):
        COMPETE = 0
        COMPETE_RES = 1
        USED_CARDS = 2
        USED_CARDS_RES = 3
        ERROR = 4
        STATUS = 5
    
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
    
    @staticmethod
    def is_valid(challenger):
        return challenger in [command.name for command in ConnectionCommand.Command]

    @staticmethod
    def parse_command(request):
        if not request:
            return None

        args = request.split(' ')
        command, args = args[0], args[1:]

        if not ConnectionCommand.is_valid(command):
            return None
        
        return ConnectionCommand(ConnectionCommand.Command[command], args)