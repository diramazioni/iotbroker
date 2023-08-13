import asyncio
import json
import logging
import websockets
from websockets.server import serve
import signal

class WebSocketServer:
    def __init__(self, interactive=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_clients = set()
        self.id = 0
        self.interactive = interactive

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
        await websockets.broadcast(self.connected_clients, message)
        # for client in self.connected_clients:
        #     await client.send(json.dumps(message))

    async def _handler(self, websocket, path):
        self.connected_clients.add(websocket)
        async for message in websocket:
            await websocket.send(json.dumps(message))
            await asyncio.sleep(0)
        try:
            await websocket.wait_closed()
            logging.debug("Websocket _handler")
            # if self.interactive:
            #     while True:
            #         await asyncio.sleep(3)  # Simulating checking for new updates

        except websockets.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            logging.error("WebSocket handler error:", e)  # Print the exception
        finally:
            self.connected_clients.remove(websocket)

    async def start(self):
        # Set the stop condition when receiving SIGTERM.
        self.loop = asyncio.get_running_loop()  # Create a new event loop
        stop = self.loop.create_future()
        self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)        
        async with serve(self._handler, "localhost", 8765):
            await stop
            #await asyncio.Future()  # run forever

async def main():
    ws = WebSocketServer(interactive=True)
    await ws.start()


if __name__ == "__main__":
    logging.basicConfig()
    file_logger = logging.FileHandler("ws.log", "w")
    formatter = logging.Formatter(
        fmt="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S "
    )
    file_logger.setFormatter(formatter)
    file_logger.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(file_logger)
    logger.setLevel(logging.DEBUG)

    start_server = asyncio.run(main())



    # def start_server(self):
    #     self.loop = asyncio.new_event_loop()  # Create a new event loop
    #     asyncio.set_event_loop(self.loop)  # Set it as the current event loop

    #     try:
    #         start_server = websockets.serve(self.websocket_handler, "localhost", 8765)
    #         self.loop.run_until_complete(start_server)  # Run the event loop
    #         self.loop.run_forever()  # Keep the event loop running
    #     except Exception as e:
    #         logging.error(f"WebSocket server error: {e}")
    #         asyncio.sleep(1)  # Wait before attempting to reconnect

