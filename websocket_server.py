import asyncio
import json
import logging
import websockets
from websockets.server import serve
import signal


class WebSocketServer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_clients = set()
        self.id = 0

    async def send_event(self, message, device=""):
        # send websocket event
        self.id += 1
        new_data = {"id": self.id, "content": message, "device": device}
        logging.debug(f"Sending WebSocket message: {new_data}")
        try:
            await self.message_all(new_data)
        except Exception as e:
            logging.error("send_event error:", e)

    async def message_all(self, message):
        try:
            # await websockets.broadcast(self.connected_clients, message)
            for client in self.connected_clients:
                await client.send(message)
        except Exception as e:
            logging.error("message_all error:", e)  # Print the exception

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
    wss = WebSocketServer()
    asyncio.create_task(wss.start())
    logging.info("WebSocketServer started...")
    if interactive:
        while True:
            await asyncio.sleep(1)  # Replace with your actual main program logic


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(interactive=True))
