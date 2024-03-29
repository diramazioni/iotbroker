import asyncio
import glob
import logging
import traceback
import websockets
from websockets.server import serve
import signal
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from websockets import WebSocketServerProtocol

"""
When send_event() is triggered, insert the new message into the DB 
and send event to all websocket connected clients
"""
cam_dir = os.path.join("www","cam")

SERVER_PATH="/ws"
HELLO_CAM = "CAM"
END_OF_STREAM = "END_OF_STREAM"

class WebSocketServer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.connected_web_clients = set()  # Set of connected web clients for the frontend
        self.connected_cam_clients = {} # Webclients for the video stream
        self.connected_esp_clients = set()  # set client list of nodes

        self.id = 0

    async def send_event(self, message):
        # send websocket event
        try:
            self.id += 1
            message_ = json.loads(message)
            ws_data = {"id": self.id, "device": message_["name"], "content": message_}
            logging.debug(f"Sending WebSocket message: {ws_data}")

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

    async def stream_image(self, device_string, message):
        try:
            for topic in self.connected_cam_clients.keys():
                if topic == device_string:
                    client = self.connected_cam_clients[device_string]
                    await client.send(message)
        except Exception as e:
            logging.error(f"image_all error:{e}")  # Print the exception


    async def save_image(self, device_string, message):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(os.path.join(cam_dir, device_string), exist_ok=True)
            filename = os.path.join(cam_dir, device_string, f"{timestamp}.jpg")
            # Write the file on disk
            with open(filename, "wb") as f:
                f.write(message)
            logging.info(f"Binary data received and saved as {filename}")                
        except Exception as e:
            logging.error(f"image_all error:{e}")  # Print the exception

    async def _handler(self, websocket, path):
        headers = websocket.request_headers
        logging.debug(f"PATH: {path}")
        logging.debug(f"request_headers: {headers}")
        user_agent = headers.get("User-Agent", "Unknown User Agent")
        path = path.replace(SERVER_PATH+"/", "") # headers.get("URI", "")

        logging.debug(f"User Agent: {user_agent}")
        camAuth = False
        camDebug = False
        device_string = ""
        binary_data = bytearray() # stores the binary data

        # Check if device is allowed to connect
        if user_agent == "TinyWebsockets Client": # Arduino client
            try:
                device_string = await asyncio.wait_for(websocket.recv(), timeout=2)
                if device_string in self.allowed_clients:
                    logging.debug(f"device_string: {device_string}")
                    camAuth = True # allow the image to be sent    
                    self.connected_esp_clients.add(websocket)
                    await websocket.send("ACK")

            except asyncio.TimeoutError:
                logging.error("WebSocket receive timed out, Cam did not say hello")
                await websocket.send("Cam not authorized")

        else: # All other client "should" be web-browser clients
            camAuth = False
            # Check if the requested path contains "cam" subscribe to video stream
            # otherwise add the client for normal messaging
            if path.startswith("cam"): # 
                device_string = path.replace("cam/", "")
                self.connected_cam_clients[device_string] = websocket
            else: # frontend clients
                self.connected_web_clients.add(websocket)
       
        try:
            async for message in websocket:
                # Handle incoming images
                if (isinstance(message, bytes) & camAuth == True):
                    # Check for the end of the stream signal
                    if END_OF_STREAM.encode() in message:
                        # Create a file when the stream is finished
                        if (camDebug == False):
                            await self.save_image(device_string, binary_data)

                        # Send the buffer to all connected_cam_clients
                        await self.stream_image(device_string, binary_data)                    
                        logging.debug(f"Binary data sent to all connected web clients")
                        # Reset binary_data for the next stream
                        binary_data = bytearray()
                    else:
                        # Append binary data to the existing buffer
                        binary_data.extend(message)
                else:
                    if str(message).startswith(HELLO_CAM):
                        logging.debug(f"CAM: {message}")
                        # toggle the debug flag to avoid saving images
                        if message == "CAM-DEBUG":
                            camDebug = not camDebug
                            logging.debug(f"DEBUG {camDebug}")
                    else:
                        # Handle text message
                        await self.send_event(message)
                        await asyncio.sleep(0)


            logging.debug("Websocket _handler")

        except websockets.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            logging.error("WebSocket handler error:", e)  # Print the exception
        finally:
            if(camAuth):
                self.connected_esp_clients.remove(websocket)
            elif path.startswith("cam"):
                device_string = path.replace("cam/", "")
                del self.connected_cam_clients[device_string]
            else:
                self.connected_web_clients.remove(websocket)

    async def start(self):
        logging.debug("WS starting********************************")
        # Load the client strings that are able to connect for sending binary images
        load_dotenv()
        self.allowed_clients = [] if os.getenv("allowed_clients") is None else os.getenv("allowed_clients").strip().split(",")
        logging.debug(self.allowed_clients)

        # Set the stop condition when receiving SIGTERM.
        self.loop = asyncio.get_event_loop()  # Create a new event loop
        stop = self.loop.create_future()
        self.loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        try:
            async with serve(self._handler, "localhost", 8765):
                logging.debug("Websocket server started********************************")
                await stop
        except OSError:
            logging.error("----------------Error: Port is already in use")
            async with serve(self._handler, "localhost", 8766):
                logging.debug("Websocket server started********************************")
                await stop
            

    async def stop(self):
        signal.raise_signal(signal.SIGTERM)

    async def updateFileList(self):
        images = {}
        for deviceType in ["field_", "robot_"]:
            pattern = deviceType + "*.jpg"
            files = glob.glob(os.path.join("www", "cam", pattern))
            files.sort()
            file_d = {file.replace("www/", ""): os.path.getctime(file) for file in files}
            images[deviceType[:-1]] = file_d
        with open(os.path.join("www", "images.json"), "w") as f:
            f.write(json.dumps(images))  # , indent=2
            f.close()

async def main(interactive=False):

    try:

        logging.info("message_parser started")
        wss = WebSocketServer()
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
