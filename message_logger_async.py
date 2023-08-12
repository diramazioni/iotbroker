import asyncio
import aiomqtt
#import paho.mqtt as mqtt
import ssl
from dotenv import load_dotenv
import os
import logging

class MessageLogger:
  
  def __init__(self) -> None:
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.DEBUG)
    self.messages = []
    load_dotenv()
    self.client_id = 'dev'
    self.MQTTS_BROKER = os.getenv("MQTTS_BROKER")
    self.MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
    self.MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
    self.MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
    self.FIWARE = os.getenv("FIWARE")
    self.ATTRS = os.getenv("ATTRS")     
    self.tls_params = aiomqtt.TLSParameters(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_NONE,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )
    
  async def _maintain_connection(self) -> None:
      reconnect_interval = 5
      while True:
          try:
              self.logger.info("Connecting to {} MQTT server".format(self.MQTTS_BROKER))
              await self.client.connect()
              self.logger.info("Connected")
          except aiomqtt.MqttError as error:
              self.logger.error(f'MQTT error "{error}". Reconnecting in {reconnect_interval} seconds.')
              await asyncio.sleep(reconnect_interval)
          except Exception as error:
              print(f'Error "{error}"..')                 

  async def __aenter__(self):
      self.client = aiomqtt.Client(
          hostname = self.MQTTS_BROKER, 
          port = self.MQTTS_PORT, 
          username = self.MQTTS_USERNAME, 
          password = self.MQTTS_PASSWORD,
          client_id = self.client_id,
          tls_params = self.tls_params,
          keepalive = 60,
      )
      await self.client.__aenter__()
      #self._reconnect_task = asyncio.create_task(self._maintain_connection())
      return self

  async def __aexit__(self, exc_type, exc_value, traceback):
      self.logger.info("Stopping MQTT")
      self._reconnect_task.cancel()
      #await self._reconnect_task
      await self.client.__aexit__(exc_type, exc_value, traceback)
      
  async def listen(self):
      reconnect_interval = 5  
      asyncio.create_task(self._maintain_connection())
      while True:
        try:  
          async with self.client.messages() as messages:
              await self.client.subscribe(f"{self.FIWARE}{self.ATTRS}") #
              self.logger.info("subscribed")
              async for message in messages:
                  message_ = message.payload.decode("utf-8")
                  self.logger.info(message_)
                  self.messages.append(message_)
        except aiomqtt.MqttError as error:
            self.logger.error(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
            await asyncio.sleep(reconnect_interval)
        except Exception as error:
            print(f'Error "{error}"..')   

async def main():
    tasks = set()
    message_logger = MessageLogger()
    try:
        async with message_logger:
          print("...")
          
          # Other things I've tried
          # L = await asyncio.gather(message_logger.listen()) # This also stops here
          
          #loop = asyncio.new_event_loop()
          #asyncio.set_event_loop(loop)
          #task = loop.create_task(message_logger.listen())    #  RuntimeWarning: coroutine 'MessageLogger.listen' was never awaited
          
          task = asyncio.create_task(message_logger.listen())                
          task.add_done_callback(tasks.discard)          
          print("add_done_callback") # never reached
          tasks.add(task)

          print("created")
          await asyncio.gather(*tasks)
          print("never reached") # never reached
          print(message_logger.messages)
    except Exception as error:
        print(f'Error "{error}"..')   


asyncio.run(main())
