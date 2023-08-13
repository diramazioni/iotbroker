import asyncio
import logging
import traceback
import websockets
from websockets.server import serve
import signal
from message_parser import MessageParser
import json

class WebSocketServer:
    def __init__(self, parser=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_clients = set()
        self.id = 0
        self.parser = parser

    async def send_event(self, message):
        # send websocket event
        self.id += 1
        device = "test"
        new_data = {"id": self.id, "content": message, "device": device}
        logging.debug(f"Sending WebSocket message: {new_data}")
        try:
            await self.parser.db_entry(json.loads(message))
            logging.info("*"*50)
            await self.message_all(message)
            logging.info("/"*50)
        except Exception as e:
            logging.error(f"send_event error:{e}")
            logging.error(traceback.format_exc())

    async def message_all(self, message):
        try:
            # await websockets.broadcast(self.connected_clients, message)
            for client in self.connected_clients:
                await client.send(message)
        except Exception as e:
            logging.error(f"message_all error:{e}")  # Print the exception

    async def _handler(self, websocket, path):
        self.connected_clients.add(websocket)
        try:
            async for message in websocket:
                await self.message_all(message)
                await asyncio.sleep(0)

            # await websocket.wait_closed()
            logging.debug("Websocket _handler")

        except websockets.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            logging.error("WebSocket handler error:", e)  # Print the exception
        finally:
            self.connected_clients.remove(websocket)

    async def start(self):
        # Set the stop condition when receiving SIGTERM.
        self.loop = asyncio.get_event_loop()  # Create a new event loop
        stop = self.loop.create_future()
        self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        async with serve(self._handler, "localhost", 8765):
            await stop


async def main(interactive=False):
    try:
        message_parser = MessageParser()
        await message_parser.connect()
        logging.info("message_parser started")    
        wss = WebSocketServer(parser=message_parser)
        asyncio.create_task(wss.start())
        logging.info("WebSocketServer started...")
        if interactive:
            while True:
                await asyncio.sleep(1)  # Replace with your actual main program logic
    except Exception as error:
        logging.error(f'Error "{error}"..')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(interactive=True))
