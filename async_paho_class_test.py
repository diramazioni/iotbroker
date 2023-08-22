import asyncio
from dotenv import load_dotenv
import os
import logging
from async_paho_mqtt_client import AsyncClient as amqtt


class MessageLogger:
    def __init__(
        self,
        id="dev",
        host="test.mosquitto.org",
        port=1883,
        username=None,
        password=None,
        tls=False,
        tls_insecure=True,
        notify_birth=False,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.client = None
        # load env vars
        load_dotenv()
        self.MQTTS_ID = os.getenv("MQTTS_ID") if os.getenv("MQTTS_ID") else id

        self.tls = tls
        self.tls_insecure = tls_insecure if tls else False
        self.keepalive = 60
        self.notify_birth = notify_birth

    async def listen(
        self,
        client_id=None,
        host=None,
        port=None,
        username=None,
        password=None,
        tls=False,
        tls_insecure=True,
        notify_birth=False,
    ):
        client = amqtt(
            host=host,
            port=port,
            username=username,
            password=password,
            client_id=client_id if client_id else __name__,
            tls=tls,
            tls_insecure=tls_insecure,
            keepalive=60,
            notify_birth=notify_birth,
        )

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
                logging.info(f"Received:{message_} from {message.topic} topic")
                # Do whatever you want with the message here
        except Exception as error:
            logging.error(f'on message Error "{error}"..')

    async def publish(self, topic, payload):
        self.client.publish(topic, payload)
        logging.info(f"Published: {payload} to {topic} topic")

    async def main(self):
        try:
            await self.listen()
            # example topic
            topic = "ACME_Utility/@json-scada/tags/#"
            await self.subscribe(topic)
            logging.info("subscribed")
            while True:
                # Here to simulate a blocking loop but you can avoid this
                # if you need to make your program flow continue

                # logging.debug(".")
                await asyncio.sleep(1)
        except Exception as error:
            logging.error(f'main Error "{error}"..')
        finally:
            self.client.stop()
            await self.client.wait_started()


async def main():
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")
    try:
        await asyncio.sleep(1)  # Replace with your actual main program logic
        message_logger = MessageLogger()
        # await message_logger.main()
        await message_logger.listen(
            host=os.getenv("MQTTS_BROKER"),
            port=int(os.getenv("MQTTS_PORT")),
            username=os.getenv("MQTTS_USERNAME"),
            password=os.getenv("MQTTS_PASSWORD"),
            tls=True,
            tls_insecure=True,
            notify_birth=True,
        )
        
        # await message_logger.listen(
        #     host="test.mosquitto.org",
        #     port=1883,
        #     tls=False,
        #     notify_birth=True,
        # )
        # topic = "ACME_Utility/@json-scada/tags/#"        
        
        topic = f"{FIWARE}{ATTRS}"
        
        logging.info(topic)
        await asyncio.sleep(1)
        await message_logger.subscribe(topic)
        imageListener = MessageLogger()
        await imageListener.listen(
            host=os.getenv("MQTT_BROKER"),
            port=int(os.getenv("MQTT_PORT")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            tls=False,
            notify_birth=True,
            client_id="imageListener"
        )
        topic = "WeLaser/PublicIntercomm/CameraToDashboard"
        await imageListener.subscribe(topic)
        
        while True:
            # logging.debug(".")
            await asyncio.sleep(1)
            
    except asyncio.exceptions.CancelledError:
        pass
    except Exception as error:
        logging.error(f'message_logger "{error}"..')




if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    asyncio.run(main())
