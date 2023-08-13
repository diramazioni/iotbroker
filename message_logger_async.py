import asyncio
import json

# import paho.mqtt as mqtt
import ssl
from dotenv import load_dotenv
import os
import logging
from async_paho_mqtt_client import AsyncClient as amqtt
from websocket_server import WebSocketServer


class MessageLogger:
    def __init__(self, id="dev", websocket=None) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        load_dotenv()
        self.MQTTS_BROKER = os.getenv("MQTTS_BROKER")
        self.MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
        self.MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
        self.MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
        self.FIWARE = os.getenv("FIWARE")
        self.ATTRS = os.getenv("ATTRS")
        self.client = None
        self.client_id = id
        self.websocket = websocket

    async def listen(self):
        # client = amqtt(
        #     host=self.MQTTS_BROKER,
        #     port=self.MQTTS_PORT,
        #     username=self.MQTTS_USERNAME,
        #     password=self.MQTTS_PASSWORD,
        #     client_id=self.client_id,
        #     tls=True,
        #     tls_insecure=True,
        #     keepalive=60,
        #     notify_birth=True
        # )

        client = amqtt(host="test.mosquitto.org", port=1883, client_id="my-client")
        await client.start()
        await client.wait_started()
        logging.info("connected")
        self.client = client

    async def subscribe(self, topic):
        await self.client.subscribe(topic)
        self.client.message_callback_add(topic, self.on_message)

    def on_message(self, client, userdata, message):
        try:
            message_ = message.payload.decode("utf-8")
            if message_:
                # message_ = json.loads(message_)
                # device = message_.topic.split(":")[3][:-6]
                logging.info(f"Received:{message_} from {message.topic} topic")

                # asyncio.create_task(self.websocket.send_event(message))
                loop = self.websocket.loop
                loop.create_task(self.websocket.message_all(message_))
        except Exception as error:
            logging.error(f'on message Error "{error}"..')

    async def main(self):
        try:
            await self.listen()
            topic = f"{self.FIWARE}{self.ATTRS}"
            topic = "ACME_Utility/@json-scada/tags/#"
            await self.subscribe(topic)
            logging.info("subscribed")
            while True:
                # logging.debug(".")
                await asyncio.sleep(1)

        except Exception as error:
            logging.error(f'Error "{error}"..')
        finally:
            self.client.stop()
            await self.client.wait_started()


async def main():
    # WebSocket non blocking start
    wss = WebSocketServer()
    asyncio.create_task(wss.start())
    logging.info("websocket started")
    await asyncio.sleep(1)  # Replace with your actual main program logic
    message_logger = MessageLogger(websocket=wss)
    try:
        await message_logger.main()
    except Exception as error:
        logging.error(f'Error "{error}"..')


logging.basicConfig()
file_logger = logging.FileHandler("messages.log", "w")
formatter = logging.Formatter(
    fmt="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S "
)
file_logger.setFormatter(formatter)
file_logger.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(file_logger)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    asyncio.run(main())
