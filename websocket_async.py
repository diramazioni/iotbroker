import asyncio
import logging
import traceback
import websockets
from websockets.server import serve
import signal
from message_parser import MessageParser
from datetime import datetime
import json

"""
When send_event() is triggered, insert the new message into the DB 
and send event to all websocket connected clients
"""


class WebSocketServer:
    def __init__(self, parser=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_clients = set()
        self.id = 0
        self.parser = parser

    async def send_event(self, message):
        # send websocket event
        try:
            self.id += 1
            message_ = json.loads(message)
            ws_data = {"id": self.id, "device": message_["name"], "content": message_}
            logging.debug(f"Sending WebSocket message: {ws_data}")

            await self.parser.db_entry(message_)
            logging.info("*" * 50)
            await self.message_all(json.dumps(ws_data))
            logging.debug(f"message_all-> {json.dumps(ws_data)}")
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
            # broadcast the message to connected clients
            async for message in websocket:
                if isinstance(message, bytes):
                    # Generate a filename with the current timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}.jpg"
                    with open(filename, "wb") as f:
                        f.write(message)
                    logging.debug(f"Binary data received and saved as {filename}")
                else:
                    # Handle text message
                    await self.message_all(message)
                    await self.send_event(message)
                    await asyncio.sleep(0)

            logging.debug("Websocket _handler")

        except websockets.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            logging.error("WebSocket handler error:", e)  # Print the exception
        finally:
            self.connected_clients.remove(websocket)

    async def start(self):
        logging.debug("WS starting********************************")
        if self.parser:
            await self.parser.connect()
        # Set the stop condition when receiving SIGTERM.
        self.loop = asyncio.get_event_loop()  # Create a new event loop
        stop = self.loop.create_future()
        self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        async with serve(self._handler, "localhost", 8765):
            logging.debug("Websocket server started********************************")
            await stop

    async def stop(self):
        if self.parser:
            await self.parser.disconnect()
            signal.raise_signal(signal.SIGTERM)


async def main(interactive=False):
    try:
        message_parser = MessageParser()
        logging.info("message_parser started")
        wss = WebSocketServer(parser=message_parser)
        asyncio.create_task(wss.start())
        logging.info("WebSocketServer started...")
        if interactive:
            while True:
                await asyncio.sleep(1)
    except Exception as error:
        logging.error(f'Error "{error}"..')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(interactive=True))
