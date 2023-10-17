import os
import asyncio
import janus

from common import constants
from network.common.connection_command import ConnectionCommand

class Client:
    def __init__(self, client_read_queue, client_write_queue):
        self.read_queue = client_read_queue
        self.write_queue = client_write_queue
        self.is_connected = False

    async def connect(self, host, delay = 0):
        await asyncio.sleep(delay)

        self.connection_reader, self.connection_writer = await asyncio.open_connection(host, constants.SERVER_PORT)
        
        self.is_connected = True
        
        self.connection_reader_task = asyncio.create_task(self.__handle_connection_reader())
        self.connection_writer_task = asyncio.create_task(self.__handle_connection_writer())

    def connected(self):
        return self.is_connected

    async def abort(self):
        self.is_connected = False
        
        try:
            asyncio.wait_for(self.connection_reader_task, timeout=1)
        except asyncio.TimeoutError:
            self.connection_reader_task.cancel()
        except asyncio.CancelledError:
            self.connection_reader_task = None

        try:
            asyncio.wait_for(self.connection_writer_task, timeout=1)
        except asyncio.TimeoutError:
            self.connection_writer_task.cancel()
        except asyncio.CancelledError:
            self.connection_writer_task = None
    
    async def __handle_connection_writer(self):
        write_queue = self.write_queue.async_q

        while self.is_connected:
            command = await write_queue.get()

            self.connection_writer.write(command.pack())
            await self.connection_writer.drain()

            write_queue.task_done()

    async def __handle_connection_reader(self):
        read_queue = self.read_queue.async_q

        while self.is_connected:
            request = await self.connection_reader.readline()
            request = request.decode('utf8').strip()

            if not request:
                break

            command = ConnectionCommand.parse_command(request)
            
            if command is not None:
                await read_queue.put(command)