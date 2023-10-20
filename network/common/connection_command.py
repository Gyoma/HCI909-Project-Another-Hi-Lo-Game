import os
from enum import Enum

class ConnectionCommand:
    """
    A class to represent all network commands needed to control the game flow
    """

    class Command(Enum):
        """
        An enumeration of all available commands
        """
        
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
        """
        Convert a command to appropriate form (array of bytes) to be sent via network 
        """
        
        return (' '.join([self._command.name, ' '.join(self._args)]) + os.linesep).encode('utf8')
    
    def __str__(self):
        return ' '.join([self._command.name, ' '.join(self._args)])

    @staticmethod
    def is_valid(name : str):
        return name in [command.name for command in ConnectionCommand.Command]

    @staticmethod
    def parse_command(request):
        """
        Parse a command from request. If it's not valid then None will be returned
        """
        
        if not request:
            return None

        args = request.split(' ')
        command, args = args[0], args[1:]

        if not ConnectionCommand.is_valid(command):
            return None
        
        return ConnectionCommand(ConnectionCommand.Command[command], args)