import asyncio
import glob
import logging
import traceback
import websockets
from websockets.server import serve
import signal
from message_parser import MessageParser
from datetime import datetime
import json
import os

"""
When send_event() is triggered, insert the new message into the DB 
and send event to all websocket connected clients
"""

allowed_clients =[]
class WebSocketServer:
    def __init__(self, parser=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_web_clients = set()
        self.connected_esp_clients = set()

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
            # await websockets.broadcast(self.connected_web_clients, message)
            for client in self.connected_web_clients:
                await client.send(message)
        except Exception as e:
            logging.error(f"message_all error:{e}")  # Print the exception

    async def _handler(self, websocket, path):
        CAM = False
        remote_ip = websocket.remote_address[0]
        try:
            # Set a timeout for receiving client_info
            client_info_timeout = 5  # adjust as needed
            device_string = await asyncio.wait_for(websocket.recv(), timeout=client_info_timeout)
            
            # Check against your allowed combinations
            if (remote_ip+'-'+device_string) in allowed_clients:
                CAM = True
                logging.info(f"CAM connected: IP {remote_ip}, Device: {device_string}")
                self.connected_esp_clients.add(websocket)
                websocket.send("ACK")
            else:
                logging.info(f"CAM unauthorized: IP {remote_ip}, Device: {device_string}")
        except asyncio.TimeoutError():
            CAM = False
            logging.info(f"Web client connection: IP {remote_ip}, Device: {device_string}")
            self.connected_web_clients.add(websocket)
            #return
        try:
            binary_data = bytearray() # stores the binary data

            async for message in websocket:
                if isinstance(message, bytes):
                    # Append binary data to the existing buffer
                    binary_data.extend(message)
                else:
                    # Check for the end of the stream signal
                    if str(message).startswith('END_OF_STREAM'):
                        # Create a file when the stream is finished
                        if binary_data:
                            device = str(message).replace('END_OF_STREAM-','')
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            os.makedirs(os.path.join("www", device), exist_ok=True)
                            filename = os.path.join("www", device, f"{timestamp}.jpg")

                            with open(filename, "wb") as f:
                                f.write(binary_data)

                            logging.debug(f"Binary data received and saved as {filename}")

                        # Reset binary_data for the next stream
                        binary_data = bytearray()
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
            if(CAM):
                self.connected_esp_clients.remove(websocket)
            else:
                self.connected_web_clients.remove(websocket)

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

    async def updateFileList(self):
        images = {}
        for deviceType in ["field_", "robot_"]:
            pattern = deviceType + "*.jpg"
            files = glob.glob(os.path.join("www", pattern))
            files.sort()
            file_d = {file.replace("www/", ""): os.path.getctime(file) for file in files}
            images[deviceType[:-1]] = file_d
        with open(os.path.join("www", "images.json"), "w") as f:
            f.write(json.dumps(images))  # , indent=2
            f.close()

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
