import asyncio
import traceback
from dotenv import load_dotenv
import os
import logging
from mqtt_async import AsyncMqttClient
from websocket_async import WebSocketServer
from message_parser import MessageParser

import json

"""
Listen to MQTT messages and echo to the WebSocket server
"""


class MQTTLogger(AsyncMqttClient):
    def __init__(self, websocket=None, log_json=False) -> None:
        super().__init__()
        self.client = None
        self.websocket = websocket
        self.log_json = log_json

    def on_message(self, client, userdata, message):
        try:
            device_name = message.topic.split(":")[-1].split("/")[0]
            message_ = message.payload.decode("utf-8")
            if message_:
                # message_ = json.loads(message_)
                # device = message_.topic.split(":")[3][:-6]
                logging.info(f"Received:{message_} from {message.topic} topic")
                # asyncio.create_task(self.websocket.send_event(message))
                if self.websocket:
                    loop = self.websocket.loop
                    loop.create_task(self.websocket.send_event(message_))
                if self.log_json:
                    asyncio.create_task(self.mess_append(device_name, message_))
        except Exception as error:
            logging.error(f'on message Error "{error}"..')

    async def mess_append(self, device, message):
        try:
            if "test" in device:
                return True
            file_name = os.path.join("data", device + ".json")
            if not os.path.exists(file_name):
                mes = []
            else:
                with open(file_name) as f:
                    mes = json.load(f)
            # append a new message to the list
            message = json.loads(message)
            mes.append(message)
            with open(file_name, "w") as f:
                f.write(json.dumps(mes))  # , indent=2
                f.close()
            # copy to the www server
            # shutil.copy(file_name, os.path.join("www", device + ".json"))
            return True
        except Exception as e:
            logging.error(f"Error in append -> {e}")

    async def main(self):
        try:
            await self.listen()
            topic = f"{self.FIWARE}{self.ATTRS}"
            # topic = "ACME_Utility/@json-scada/tags/#"
            await self.subscribe(topic)
            logging.info("subscribed")
            await asyncio.sleep(1)
            # exit or loop forever
        except Exception as error:
            logging.error(f'main Error "{error}"..')
        finally:
            await self.client.stop()
            await self.client.wait_started()


# Actual main
async def main(interactive=False):
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")
    CLIENT_ID = os.getenv("CLIENT_ID") + "_mqtt_logger"

    try:
        message_parser = MessageParser()
        wss = WebSocketServer(parser=message_parser)
        asyncio.create_task(wss.start())
        mqtt_logger = MQTTLogger(
            websocket=wss,
            log_json=False,
        )
        logging.info("WebSocketServer started...")

        await mqtt_logger.listen(
            host=os.getenv("MQTTS_BROKER"),
            port=int(os.getenv("MQTTS_PORT")),
            username=os.getenv("MQTTS_USERNAME"),
            password=os.getenv("MQTTS_PASSWORD"),
            tls=True,
            tls_insecure=True,
            client_id=CLIENT_ID,
            notify_birth=True,
        )
        topic = f"{FIWARE}{ATTRS}"
        await mqtt_logger.subscribe(topic)
        while True:
            # logging.debug(".")
            await asyncio.sleep(1)
    except asyncio.exceptions.CancelledError:
        pass
    except Exception as error:
        logging.error(f'mqtt_logger "{error}"..')
        logging.error(traceback.format_exc())
    finally:
        await mqtt_logger.client.stop()
        await mqtt_logger.client.wait_started()
        await wss.stop()


# logging.basicConfig()
# file_logger = logging.FileHandler("messages.log", "w")
# formatter = logging.Formatter(
#     fmt="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S "
# )
# file_logger.setFormatter(formatter)
# file_logger.setLevel(logging.INFO)
# logger = logging.getLogger()
# logger.addHandler(file_logger)
# logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(interactive=False))
