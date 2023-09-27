import logging
import os
import shutil
import time
import traceback

from dotenv import load_dotenv
import asyncio
import json
import glob

from mqtt_async import AsyncMqttClient
from ftp_async import AsyncFtpClient

"""
Listen for image message and re-publish with ImagePublisher
"""

PATH_ROBOT = "/robot_images"
PATH_FIELD = "/field_images"


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
        self.ftp_download_done = False
        self.ftp_upload_done = False

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        topic = message.topic
        logging.info(f"MQTT on_message: Topic: {topic}, Payload: {payload}")
        content = json.loads(payload)
        # device_name = topic.split(":")[-1].split("/")[0]
        if content["packetType"] == "picture":
            device = content["nodeId"]
            picture = content["data"]
            # FTP download
            remotePath = ""
            if "camera" in device:
                remotePath = PATH_FIELD
            elif "robot" in device:
                remotePath = PATH_ROBOT
            else:
                logging.error(f"Unknown device {device}")
                return
            asyncio.create_task(self.ftp_copy(remotePath, device, picture))

    def download_done(self, future):
        logging.debug("@@@ download_done")
        self.ftp_download_done = True

    def upload_done(self, future):
        logging.debug("@@@ upload_done")
        self.ftp_upload_done = True

    async def ftp_download(self, remotePath, picture):
        self.ftp_download_done = False
        try:
            await self.ftp_from.connect()
            logging.debug(f"connected ftp_retr {remotePath}")
            await self.ftp_from.retrieveFile(remotePath, picture)
            await self.ftp_from.disconnect()
            logging.debug("ftp_download done")
            self.ftp_download_done = True
            # deviceType = remotePath[1:].replace("images", "")
            # await self.updateFileList()

        except Exception as e:
            logging.error(f"Error ftp_download -> {e}")

    async def ftp_upload(self, remotePath, picture):
        self.ftp_upload_done = False
        try:
            await self.ftp_to.connect()
            logging.debug(f"connected ftp_upload {remotePath}")
            await self.ftp_to.sendFile(remotePath, picture)
            await self.ftp_to.disconnect()
            logging.debug("ftp_upload done")
            self.ftp_upload_done = True
        except Exception as e:
            logging.error(f"Error ftp_upload -> {e}")

    async def ftp_copy(self, remotePath, device, picture):
        download_task = asyncio.create_task(self.ftp_download(remotePath, picture))
        download_task.add_done_callback(self.download_done)
        await download_task
        upload_task = asyncio.create_task(self.ftp_upload(remotePath, picture))
        upload_task.add_done_callback(self.upload_done)
        await upload_task

        # await self.ftp_upload(remotePath, picture)
        if self.ftp_upload_done:
            # Publish to MQTTS broker
            await self.publishToMqtts(device, picture)
            if "field" in remotePath:
                device = "field_" + device
            shutil.move(  # server www
                picture, os.path.join(os.getcwd(), "www", device + ".jpg")
            )
            await self.updateFileList()

    async def publishToMqtts(self, device, picture):
        timestamp = time.time()
        dev_ = "Camera:"
        ptopic = f"{self.FIWARE}{self.ENTITY}{dev_}{device}/attrs"
        id = f"{self.ENTITY}{dev_}{device}"
        new_payload = {
            "id": id,
            "name": device,
            "timestamp": timestamp,
            "picture": picture,
            "type": "Camera",
        }

        self.publisher.queue.put_nowait((ptopic, json.dumps(new_payload)))
        self.counter += 1
        logging.info(f"Sent {self.counter} messages")

    async def updateFileList(self):
        logging.debug(f"updateFileList")
        images = {}
        for p in [PATH_FIELD, PATH_ROBOT]:
            deviceType = p[1:].replace("images", "")
            pattern = deviceType + "*.jpg"
            files = glob.glob(os.path.join("www", pattern))
            files.sort()
            # files.sort(key=lambda x: os.path.getctime(x), reverse=True)
            file_d = {
                file.replace("www/", ""): os.path.getctime(file) for file in files
            }
            images[deviceType[:-1]] = file_d
        with open(os.path.join("www", "images.json"), "w") as f:
            f.write(json.dumps(images))  # , indent=2
            f.close()


def updateFileList():
    images = {}
    for p in [PATH_FIELD, PATH_ROBOT]:
        deviceType = p[1:].replace("images", "")
        pattern = deviceType + "*.jpg"
        files = glob.glob(os.path.join("www", pattern))
        files.sort()
        # files.sort(key=lambda x: os.path.getctime(x), reverse=True)
        # files = [file.replace('www/', '') for file in files]
        file_d = {file.replace("www/", ""): os.path.getctime(file) for file in files}
        images[deviceType[:-1]] = file_d
    with open(os.path.join("www", "images.json"), "w") as f:
        f.write(json.dumps(images))  # , indent=2
        f.close()


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
            client_id=CLIENT_ID + "_imagePublisher",
            notify_birth=True,
        )
        # ImageListener: Listen for image message and re-publish with ImagePublisher
        imageListener = ImageListener(
            publisher=imagePublisher,
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
            client_id=CLIENT_ID + "_imageListener",
            notify_birth=True,
        )
        topic = "WeLaser/PublicIntercomm/CameraToDashboard"
        await imageListener.subscribe(topic)
        logging.info("I" * 80)
        logging.info("ImageListener started")

        logging.info("ImagePublisher started processing messages")
        counter = 0
        while True:
            # Here ends the flow, it'll keep watching if new message arrives and publish to MQTTS
            await imagePublisher.publishQueue()
            counter += 1
            if counter > 3600:  # restart the program every hour
                break
            await asyncio.sleep(1)

    except Exception as error:
        logging.error(f'Error "{error}"..')
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
