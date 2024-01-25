#Note demo scripts have limited or no error detection and use
#timers to wait for events. They assume everything works ok
#www.steves-internet-guide.com
#contact steve@steves-internet-guide.com
#uses websockets publish-subscribe and receive message
import logging
import paho.mqtt.client as paho
import time
broker="greenlab.unibo.it"
port = 443
#broker="test.mosquitto.org"
#port = 8081

sub_topic="house/#"

def on_subscribe(client, userdata, mid, granted_qos):   
   print("subscribed with qos",granted_qos, "\n")
   pass
   
def on_message(client, userdata, message):
    print("message received  "  , str(message.payload.decode("utf-8")))
    
def on_publish(client,userdata,mid):   
   print("data published mid=",mid, "\n")
   pass
   
def on_disconnect(client, userdata, rc):
   print("client disconnected ok") 
   
client=paho.Client("client-id", transport='websockets')      

client.tls_set()
# client.tls_insecure_set(True)
client.ws_set_options(path="/mqtt")
client.enable_logger()
client.on_subscribe = on_subscribe       #assign function to callback
client.on_publish = on_publish        #assign function to callback
client.on_message = on_message        #assign function to callback
client.on_disconnect = on_disconnect
print("connecting to broker ", broker, "on port ",port)
client.connect(broker,port)           #establish connection
client.loop_start()
print("subscribing to ",sub_topic)
client.subscribe(sub_topic)
time.sleep(3)
client.publish("house/bulb1","on")    #publish
time.sleep(4)

client.disconnect()

