import asyncio
import aiomqtt
import paho.mqtt as mqtt
import ssl
from dotenv import load_dotenv
import os

class MessageLogger:
  
  async def init(self):
    await self.load_env_variables()
    self.tls_params = aiomqtt.TLSParameters(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_NONE,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )
    
  async def load_env_variables(self):
      load_dotenv()
      self.MQTTS_BROKER = os.getenv("MQTTS_BROKER")
      self.MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
      self.MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
      self.MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
      self.FIWARE = os.getenv("FIWARE")
      self.ENTITY = os.getenv("ENTITY")      
      
  async def mqttListen(self):
      await self.init()
      
      reconnect_interval = 5  # In seconds
      while True:
          try:  
            async with aiomqtt.Client(
              hostname=self.MQTTS_BROKER, 
              port=self.MQTTS_PORT, 
              username=self.MQTTS_USERNAME, 
              password=self.MQTTS_PASSWORD,
              tls_params=self.tls_params) as client:
                async with client.messages() as messages:
                    await client.subscribe(f"{self.FIWARE}+/attrs") #
                    print("sub")
                    async for message in messages:
                        print(message.payload.decode("utf-8"))
          except aiomqtt.MqttError as error:
              print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
              await asyncio.sleep(reconnect_interval)

  async def main(self):
    async with asyncio.TaskGroup() as tg:
      # Wait for messages in (unawaited) asyncio task
      #loop = asyncio.get_event_loop()
      tg.create_task(self.mqttListen())
      print("...")
      #await task

ml = MessageLogger()
asyncio.run(ml.main())