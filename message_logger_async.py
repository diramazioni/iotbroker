import asyncio

# import paho.mqtt as mqtt
import ssl
from dotenv import load_dotenv
import os
import logging
from async_paho_mqtt_client import AsyncClient as amqtt


class MessageLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        load_dotenv()
        self.client_id = "dev"
        self.MQTTS_BROKER = os.getenv("MQTTS_BROKER")
        self.MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
        self.MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
        self.MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
        self.FIWARE = os.getenv("FIWARE")
        self.ATTRS = os.getenv("ATTRS")
        self.client = None

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
        # )
        client = amqtt(
            host="test.mosquitto.org", 
            port=1883, 
            client_id="my-client"
        )        
        await client.start()
        await client.wait_started()
        self.client = client

    async def subscribe(self, topic):
        await self.client.subscribe(topic)
        self.client.message_callback_add(topic, self.on_message)

    def on_message(self, client, userdata, message):
        print(f"Received {message.payload.decode('utf-8')} from {message.topic} topic")

    async def main(self):
        try:
            await self.listen()
            # topic = f"{self.FIWARE}{self.ATTRS}"
            topic = "ACME_Utility/@json-scada/tags/#"
            await self.subscribe(topic)
            while True:
                await asyncio.sleep(1)

        except Exception as error:
            print(f'Error "{error}"..')
        finally:
            self.client.stop()
            await self.client.wait_started()


async def main():
    message_logger = MessageLogger()
    try:
        await message_logger.main()
    except Exception as error:
        print(f'Error "{error}"..')


if __name__ == "__main__":
    asyncio.run(main())

