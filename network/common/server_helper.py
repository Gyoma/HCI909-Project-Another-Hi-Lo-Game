import subprocess
import sys
import os

from network.common import server_constants
from network.common.connection_command import ConnectionCommand

def is_command(challenger):
    return challenger in [command.name for command in ConnectionCommand.Command]

def parse_command(request):
    args = request.split(' ')
    command, args = args[0], args[1:]

    if not is_command(command):
        return None
    
    return ConnectionCommand(ConnectionCommand.Command[command], args)

def is_card(challenger):
    return challenger in server_constants.CARD_NAMES