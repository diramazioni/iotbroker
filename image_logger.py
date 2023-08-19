import logging
import os
import time

from dotenv import load_dotenv
import asyncio
import json

from mqtt_logger import MessageLogger  # Import your original MessageLogger class
from ftp_async import AsyncFtpClient

"""
Listen for image message and re-publish with ImagePublisher
"""


class ImageListener(MessageLogger):
    def __init__(
        self,
        publisher=None,
        ftp_from=None,
        ftp_to=None,
        fiware=None,
        entity=None,
        log_json=False,
    ) -> None:
        super().__init__(log_json=log_json)
        self.publisher = publisher
        self.FIWARE = fiware
        self.ENTITY = entity
        self.ftp_from = ftp_from
        self.ftp_to = ftp_to

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        topic = message.topic
        logging.info(f"Custom on_message: Topic: {topic}, Payload: {payload}")
        content = json.loads(payload)
        device = content["nodeId"]
        picture = content["data"]
        device_name = topic.split(":")[-1].split("/")[0]
        if content["packetType"] == "picture":
            # FTP copy
            asyncio.create_task(self.ftp_copy(device_name, picture))
            
            # Publish to MQTTS broker
            timestamp = time.time()
            dev_ = "Camera:"
            ptopic = f"{self.FIWARE}{self.ENTITY}{dev_}{device}/attrs"
            id = f"{self.ENTITY}{dev_}{device}"
            payload = {
                "id": id,
                "name": device_name,
                "timestamp": timestamp,
                "picture": picture,
            }
            asyncio.create_task(self.publisher.publish(ptopic, payload))

    async def ftp_copy(self, device, picture):
        remotePath = ""
        PATH_ROBOT = "/robot_images"
        PATH_FIELD = "/field_images"
        if "camera" in device:
            remotePath = PATH_FIELD
        elif "robot" in device:
            remotePath = PATH_ROBOT
        else:
            logging.error(f"Unknown device {device}")
            return

        try:
            await self.ftp_from.connect()
            logging.debug("connected ftp from")
            await self.ftp_from.retrieveFile(remotePath, picture)
            await self.ftp_from.disconnect()
            logging.debug("ftp 1 done")
        except Exception as e:
            logging.error(f"Error in Ftp1 -> {e}")
        try:
            await self.ftp_to.connect()
            logging.debug("connected ftp to")
            await self.ftp_to.sendFile(remotePath, picture)
            await self.ftp_to.disconnect()
            logging.debug("ftp 2 done")
        except Exception as e:
            logging.error(f"Error in Ftp2 -> {e}")
            
            

"""
Publish image to MQTTS broker
"""


class ImagePublisher(MessageLogger):
    def __init__(self, log_json=False) -> None:
        super().__init__(log_json=log_json)


""" MAIN """


async def main(interactive=False):
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")

    try:
        ftp_from = AsyncFtpClient(
            host=os.getenv("HOST_FROM"),
            port=int(os.getenv("PORT_FROM")),
            username=os.getenv("USER_FROM"),
            password=os.getenv("PASS_FROM"),
        )
        ftp_to = AsyncFtpClient(
            host=os.getenv("HOST_TO"),
            port=int(os.getenv("PORT_TO")),
            username=os.getenv("USER_TO"),
            password=os.getenv("PASS_TO"),
        )
        imagePublisher = ImagePublisher()
        await imagePublisher.listen(
            host=os.getenv("MQTTS_BROKER"),
            port=int(os.getenv("MQTTS_PORT")),
            username=os.getenv("MQTTS_USERNAME"),
            password=os.getenv("MQTTS_PASSWORD"),
            tls=True,
            tls_insecure=True,
            notify_birth=True,
        )
        # ImageListener: Listen for image message and re-publish with ImagePublisher
        imageListener = ImageListener(
            publisher=ImagePublisher,
            ftp_from=ftp_from,
            ftp_to=ftp_to,
            fiware=FIWARE,
            entity=ENTITY,
            log_json=True,
        )
        await imageListener.listen(
            host=os.getenv("MQTT_BROKER"),
            port=int(os.getenv("MQTT_PORT")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            tls=False,
            notify_birth=True,
        )
        topic = f"{FIWARE}{ATTRS}"
        await imageListener.subscribe(topic)
        logging.info("I" * 80)
        logging.info("ImageListener started")
        if interactive:
            while True:
                await asyncio.sleep(1)
    except Exception as error:
        logging.error(f'Error "{error}"..')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(interactive=True))
