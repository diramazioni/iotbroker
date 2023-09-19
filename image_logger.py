import logging
import os
import shutil
import time
import traceback

from dotenv import load_dotenv
import asyncio
import json

from mqtt_async import AsyncMqttClient
from ftp_async import AsyncFtpClient

"""
Listen for image message and re-publish with ImagePublisher
"""


class ImageListener(AsyncMqttClient):
    def __init__(
        self,
        publisher=None,
        ftp_from=None,
        ftp_to=None,
        fiware=None,
        entity=None,
        log_json=False,
    ) -> None:
        super().__init__()
        self.publisher = publisher
        self.FIWARE = fiware
        self.ENTITY = entity
        self.ftp_from = ftp_from
        self.ftp_to = ftp_to
        self.counter = 0

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        topic = message.topic
        logging.info(f"MQTT on_message: Topic: {topic}, Payload: {payload}")
        content = json.loads(payload)
        device = content["nodeId"]
        picture = content["data"]
        # device_name = topic.split(":")[-1].split("/")[0]
        if content["packetType"] == "picture":
            # FTP copy
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
            # FTP download
            asyncio.create_task(self.ftp_download(remotePath, device, picture))
            # Publish to MQTTS broker
            timestamp = time.time()
            dev_ = "Camera:"
            ptopic = f"{self.FIWARE}{self.ENTITY}{dev_}{device}/attrs"
            id = f"{self.ENTITY}{dev_}{device}"
            new_payload = {
                "id": id,
                "name": device,
                "timestamp": timestamp,
                "picture": picture,
                "type": "Camera"
            }
            
            self.publisher.queue.put_nowait((ptopic, json.dumps(new_payload)))
            self.counter += 1
            logging.info(f"Sent {self.counter} messages")
            # let's disable ftp upload for now!!!
            # FTP upload
            #asyncio.create_task(self.ftp_upload(remotePath, picture))

    async def ftp_download(self, remotePath, device, picture):
        try:
            await self.ftp_from.connect()
            logging.debug(f"connected ftp_retr {remotePath}")
            await self.ftp_from.retrieveFile(remotePath, picture)
            await self.ftp_from.disconnect()
            logging.debug("ftp_download done")
            deviceType = remotePath[1:].replace("images", "")

            shutil.move(  # server www
                picture, os.path.join(os.getcwd(), "www", deviceType + device + ".jpg")
            )

        except Exception as e:
            logging.error(f"Error ftp_download -> {e}")

    async def ftp_upload(self, remotePath, picture):
        try:
            await self.ftp_to.connect()
            logging.debug(f"connected ftp_upload {remotePath}")
            await self.ftp_to.sendFile(remotePath, picture)
            await self.ftp_to.disconnect()
            logging.debug("ftp_upload done")
        except Exception as e:
            logging.error(f"Error ftp_upload -> {e}")

    async def ftp_copy(self, remotePath, picture):
        await self.ftp_download(remotePath, picture)
        await self.ftp_upload(remotePath, picture)



""" MAIN """


async def main(interactive=False):
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")
    CLIENT_ID = os.getenv("CLIENT_ID") 
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
        imagePublisher = AsyncMqttClient()
        await imagePublisher.listen(
            host=os.getenv("MQTTS_BROKER"),
            port=int(os.getenv("MQTTS_PORT")),
            username=os.getenv("MQTTS_USERNAME"),
            password=os.getenv("MQTTS_PASSWORD"),
            tls=True,
            tls_insecure=True,
            client_id=CLIENT_ID+"_imagePublisher",
            notify_birth=True
        )
        # ImageListener: Listen for image message and re-publish with ImagePublisher
        imageListener = ImageListener(
            publisher=imagePublisher,
            ftp_from=ftp_from,
            ftp_to=ftp_to,
            fiware=FIWARE,
            entity=ENTITY,
            log_json=True
        )
        await imageListener.listen(
            host=os.getenv("MQTT_BROKER"),
            port=int(os.getenv("MQTT_PORT")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            tls=False,
            client_id=CLIENT_ID+"_imageListener",
            notify_birth=True
        )
        topic = "WeLaser/PublicIntercomm/CameraToDashboard"
        await imageListener.subscribe(topic)
        logging.info("I" * 80)
        logging.info("ImageListener started")

        logging.info("ImagePublisher started processing messages")
        while True:
            # Here ends the flow, it'll keep watching if new message arrives and publish to MQTTS
            await imagePublisher.publishQueue()
            await asyncio.sleep(1)

    except Exception as error:
        logging.error(f'Error "{error}"..')
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
