import asyncio
import traceback
from dotenv import load_dotenv
import os
import logging
from async_paho_mqtt_client import AsyncClient 
import uuid
import json

class AsyncMqttClient:
    def __init__(self) -> None:
        self.client = None
        self.loop = None
        self.queue = None
        
    async def listen(
        self,
        client_id=None,
        host=None,
        port=None,
        username=None,
        password=None,
        tls=False,
        tls_insecure=True,
        notify_birth=False
    ):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.client = AsyncClient(
            host=host,
            port=port,
            username=username,
            password=password,
            client_id=client_id if client_id else f"{__name__}-{str(uuid.uuid4()).split('-')[0]}",
            tls=tls,
            tls_insecure=tls_insecure,
            keepalive=60,
            notify_birth=notify_birth
        )

        await self.client.start()
        await self.client.wait_started()
        logging.info("connected")
        

    async def subscribe(self, topic):
        await self.client.subscribe(topic)
        logging.info(f"Subriscribed: {topic} ")
        self.client.message_callback_add(topic, self.on_message)

    def on_message(self, client, userdata, message):
        try:
            message_ = message.payload.decode("utf-8")
            if message_:
                logging.info(f"Received:\n{message_} from \n{message.topic} topic")
                # Do whatever you want with the message here
        except Exception as error:
            logging.error(f'on message Error "{error}"..')

    async def publish(self, topic, payload):
        await self.client.publish_noid(topic, payload)
        logging.info(f"Published: \n{payload}\n to topic:\n{topic} ")

    async def publishQueue(self):
        while (self.queue.qsize() > 0):
            topic, payload = await self.queue.get()
            await self.client.publish_noid(topic, payload)
            logging.info(f"Queue published: \n{payload}\n to topic:\n{topic} ")

    async def main(self):
        logging.info("Starting main loop")
        try:
            while True:
                await self.publishQueue()
                await asyncio.sleep(1)
        except Exception as error:
            logging.error(f'main Error "{error}"..')


async def main():
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")
    try:
        await asyncio.sleep(1)  # Replace with your actual main program logic
        message_logger = AsyncMqttClient()
        # await message_logger.main()
        await message_logger.listen(
            host=os.getenv("MQTTS_BROKER"),
            port=int(os.getenv("MQTTS_PORT")),
            username=os.getenv("MQTTS_USERNAME"),
            password=os.getenv("MQTTS_PASSWORD"),
            tls=True,
            tls_insecure=True,
            notify_birth=True,
            client_id="message_logger",
        )
        loop = message_logger.loop
        loop.create_task(message_logger.main())

        topic = "message_logger_test"
        for i in range(5):
            payload = {"message": f"Hello World {i}"}
            await message_logger.queue.put((topic, json.dumps(payload)))
            await asyncio.sleep(0.1)
        
    except asyncio.exceptions.CancelledError:
        pass
    except Exception as error:
        logging.error(f'message_logger "{error}"..')
        logging.error(traceback.format_exc())



if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    asyncio.run(main())
