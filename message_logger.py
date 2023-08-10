import os
import sys

import paho.mqtt.client as mqttClient
import json
import ssl
import time
from time import strftime, localtime
from dotenv import load_dotenv
import logging
from threading import Thread
import asyncio
import websockets

from sensor_processor_async import SensorProcessor
class MessageLogger:
    def __init__(self):
        self.id = 0
        self.loop = None
        self.db_loop = None
        self.connected_clients = set()
        self.load_env_variables()
        self.mqtts_client = mqttClient.Client()
        self.mqtts_client.username_pw_set(self.MQTTS_USERNAME, password=self.MQTTS_PASSWORD)
        self.mqtts_client.on_connect = self.on_mqtts_connect
        self.mqtts_client.on_publish = self.on_mqtts_publish
        self.mqtts_client.on_message = self.on_mqtts_message
        self.mqtts_client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_NONE,  
            tls_version=ssl.PROTOCOL_TLSv1_2,
            ciphers=None,
        )
        self.mqtts_client.tls_insecure_set(True)  # <<<<<<<< MQTTS cert not Valid bypass
        self.db = SensorProcessor()


    def load_env_variables(self):
        load_dotenv()
        self.MQTTS_BROKER = os.getenv("MQTTS_BROKER")
        self.MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
        self.MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
        self.MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
        self.FIWARE = os.getenv("FIWARE")
        self.ENTITY = os.getenv("ENTITY")
        self.PATH_LOCAL = os.getcwd()
    
    
    def MQTTS_connect(self, MQTTS_username, MQTTS_password, broker_endpoint, port):
      self.mqtts_client.connect(broker_endpoint, port=port)
      self.mqtts_client.loop_start()
      # mqtts_client.loop_forever()
      attempts = 0
      while not self.mqtts_client.is_connected() and attempts < 5:  # Wait for connection
          logging.debug("mqtts waiting to connect...")
          time.sleep(1)
          attempts += 1

      if not self.mqtts_client.is_connected():
          logging.error("Could not connect to broker")
          return False
      return True
    # subscribe to MQTT
    def mqtt_subscribe(self, client, topic):
        try:
            # OVERLAY stopic -> SUBSCRIBE ALL
            client.subscribe(topic)
        except Exception as e:
            logging.error(f"[ERROR] Could not subscribe: {e}")    
        logging.debug("subscribed")
            
    def on_mqtts_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTTS broker - CESENA")
        else:
            logging.error("Error, MQTTS connection failed")
            
    def on_mqtts_publish(self, client, userdata, result):
        pass
    
    def on_mqtts_message(self, client, userdata, result):
      try:
        message = result.payload.decode("utf-8")
        device = result.topic.split(":")[3][:-6]
        logging.info(f"New MQTTS message on {device}: {message}")
        message_ = json.loads(message)
        # Create a new entry in the db    
        #asyncio.run(self.db.db_entry(message_))
        self.send_websocket_event(message_, device)
      except Exception as e:
        logging.error("create DB entry error:", e)  
      return True
    
    
    # WebSocket
    def send_websocket_event(self, message, device=""):
      # send websocket event
      self.id += 1
      new_data = {"id": self.id, "content": message, "device": device }
      logging.debug(f"Sending WebSocket message: {new_data}")
      try:
        ##################################################################
        #asyncio.set_event_loop(self.db_loop)
        #self.db_loop.create_task(self.db.db_entry(message))
        #asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.send_update_to_clients(new_data))
      except Exception as e:
        logging.error("send_websocket_event error:", e)  
    
    async def send_update_to_clients(self, update):
        for client in self.connected_clients:
            await client.send(json.dumps(update))

    async def websocket_handler(self, websocket, path):
        self.connected_clients.add(websocket)
        try:
            while True:
                await asyncio.sleep(3)  # Simulating checking for new updates
                # await websocket.recv()
                new_data = {"id": 123, "content": "debug message"}
                #await self.send_update_to_clients(new_data)
        except websockets.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            logging.error("WebSocket handler error:", e)  # Print the exception          
        finally:
            self.connected_clients.remove(websocket)

    def start_websocket_server(self):
        self.loop = asyncio.new_event_loop()  # Create a new event loop
        asyncio.set_event_loop(self.loop)  # Set it as the current event loop
        
        try:
            start_server = websockets.serve(self.websocket_handler, "localhost", 8765)
            self.loop.run_until_complete(start_server)  # Run the event loop
            self.loop.run_forever()  # Keep the event loop running
        except Exception as e:
            logging.error(f"WebSocket server error: {e}")
            time.sleep(1)  # Wait before attempting to reconnect
    
    def main(self, interactive=False):
      logging.debug("main()")
      try:
        self.MQTTS_connect(self.MQTTS_USERNAME, self.MQTTS_PASSWORD, self.MQTTS_BROKER, self.MQTTS_PORT)
        #if connected:
        stopic = f"{self.FIWARE}+/attrs"
        self.mqtt_subscribe(self.mqtts_client, stopic)
        
        # Start the WebSocket server in a separate thread
        websocket_server_thread = Thread(target=self.start_websocket_server)
        websocket_server_thread.start()

        # Connect to db
        #self.loop.create_task(self.db.connect())
        #self.db_loop = asyncio.new_event_loop()  # Create a new event loop
        #asyncio.set_event_loop(self.db_loop)
        #asyncio.run(self.db.connect())
        #newfeature = asyncio.get_event_loop().run_until_complete(self.db.connect())

        #self.loop.create_task()
        

        if interactive:
          in_ = ""
          while in_ not in ["x", "X"]:
              print("\/" * 10 + "    WAITING FOR INPUT    " + "\/" * 10)
              in_ = input(
                  '"x" to exit., \n"a" test websocket \n'
              )
              print("\/" * 40)
              if in_ in ["a", "A"]:
                  content = {
                      "id": "urn:ngsi-ld:Device:WeatherStation_v8", 
                      "name": "WeatherStation_v8", 
                      "areaServed": "urn:ngsi-ld:AgriFarm:007", 
                      "location": {"coordinates": [5.1729, 51.366], "type": "Point"}, 
                      "timestamp": 1691600400000, 
                      "controlledProperty": ["temperature", "humidity", "pressure", "wind_speed", "wind_deg", "rain"], 
                      "value": [19.79, 61, 1018, 4.55, 300, 0], 
                      "units": ["degC", "%", "mBar", "m/s", "degNcw", "mm"]
                    }
                  message = {"id": 1234, 'device': 'TEST', "content": content}
                  
                  #self.send_websocket_event(message)
                  ptopic = f"{self.FIWARE}{self.ENTITY}device:test/attrs"
                  self.mqtts_client.publish(ptopic, content)
                  #asyncio.set_event_loop(self.db_loop)
                  #self.db_loop.create_task(self.db.db_entry(message["content"]))
                  logging.info("sent websocket event")
                  
              elif in_ in ["x", "X"]:
                sys.exit(0)
      except KeyboardInterrupt:
        pass
      finally:
          self.mqtts_client.loop_stop()
          websocket_server_thread.join()
          asyncio.set_event_loop(self.loop)
          self.loop.create_task(self.db.disconnect()) 
          sys.exit(0)
          
# Logging config
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
    message_logger = MessageLogger()
    try:
        message_logger.main(interactive=True)
    except Exception as e:
        logging.error(f"Error {e}")
    finally:
        message_logger.mqtts_client.loop_stop()
        sys.exit(1)
