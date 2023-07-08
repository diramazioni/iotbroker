'''
WELASER - by GV June 2023
Capture messages from  Ardesia MQTT (insecure)
and publish them to WeLASER MQTTS (over TLS)
then parse MQTT message, extract FTP file name and copy
the files from  Ardesia to Local and to WeLASER
Further on capture messages from MQTTS and
append them to device.txt
Finally publish a TEST message on MQTTS 
'''
import os
import threading
import paho.mqtt.client as mqttClient
import json
#import ast # to convert string into dictionary
import ssl
from ftplib import FTP, all_errors
import time
from time import strftime, localtime
#from datetime import datetime  # datetime data type

from dotenv import load_dotenv # legge codici di accesso
import shutil
#  ==========================================
#          LOADS ENVIROMENT VARIABLES
load_dotenv()
# MQTT at ardesia
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')   # Put here your Ubidots TOKEN
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')  # Leave this in blank
# MQTTS
# BROKER MQTTS at  "csi-traffic.campusfc.unibo.it"
MQTTS_BROKER = os.getenv('MQTTS_BROKER')
MQTTS_PORT = int(os.getenv('MQTTS_PORT'))
MQTTS_USERNAME = os.getenv('MQTTS_USERNAME')
MQTTS_PASSWORD = os.getenv('MQTTS_PASSWORD')
# FTPs
HOST_TO = os.getenv('HOST_TO')
PORT_TO = int(os.getenv('PORT_TO'))
USER_TO = os.getenv('USER_TO')
PASS_TO = os.getenv('PASS_TO')

HOST_FROM = os.getenv('HOST_FROM')
PORT_FROM = int(os.getenv('PORT_FROM'))
USER_FROM = os.getenv('USER_FROM')
PASS_FROM = os.getenv('PASS_FROM')


PATH_LOCAL = os.getenv('PATH_LOCAL')
FIWARE = os.getenv('FIWARE')
ENTITY = os.getenv('ENTITY')

#  ==========================================
#                global variables

PATH_ROBOT = "/robot_images"
PATH_FIELD = "/field_images"



stopic1 = "WeLaser/PublicIntercomm/CameraToDashboard"
stopic2 = "WeLaser/PublicIntercomm/RobotToDashboard"

mqtts_client = mqttClient.Client()
mqtt_client = mqttClient.Client()

mqtt_connected = False  # Stores the connection status
mqtts_connected = False  # Stores the connection status
device = ""
picture = ""
remotePath = ""
#  ==========================================
#                   Functions
#  ========================================== 
#                    MQTT(S)
#--------------------------------------------
def on_mqtt_connect(client, userdata, flags, rc):
    #global mqtt_connected  # Use global variable
    if rc == 0:
        print("[INFO] Connected to MQTT broker - ARDESIA")
        mqtt_connected = True  # Signal connection
    else:
        print("[INFO] Error, connection failed")

# -------------------------------------------------
def on_mqtts_connect(client, userdata, flags, rc):
    #global mqtts_connected  # Use global variable
    if rc == 0:
        print("[INFO] Connected to MQTTS broker - WeLASER")
        mqtts_connected = True  # Signal connection
    else:
        print("[INFO] Error, connection failed")

# -------------------------------------------------
def on_mqtt_publish(client, userdata, result):
    print("MQTT Published!")

# -------------------------------------------------
def on_mqtts_publish(client, userdata, result):
    print("MQTTS Published!")
    
# -------------------------------------------------
def on_mqtt_message(client, userdata, result):
    #global device
    #global picture
    #global remotePath
     # Here Persistency could be configured -> always receive the same message ""
    message = str(result.payload.decode("utf-8")).replace(" ", "").replace("\'", "\"").replace('/n', '')
    print("---------vvvvvv ---- New Message on MQTT !")
    print( "message:" + message )
    print("---------^^^^^^")

# PARSING - deserialising
    content = json.loads(message)
    device = content['nodeId']
    print('device = nodeId:',device)  
    packetType = content['packetType']
    print('packetType:',packetType)  
    if (packetType == "picture") :
        picture = content['data'] 
        print( ">>>>>>>>>>>>>> WITH PICTURE:" + picture ) 
# verifico chi produce l'immagine     
        camType = device[0:5]   # camtype = [camer | robot]
        print(" >>>> CAM >>>>> ",camType)
        # es> paths should be built using os.path.join(path1, subdir, etc)
        remotePath = ""
        if camType == "camer":
            remotePath  = PATH_FIELD
        elif camType == "robot":
            remotePath  = PATH_ROBOT
# ----------------------------------- INVIO FTP
        x = threading.Thread(target=ftp_bounce, args=(remotePath,device,picture,))
        x.start()
        #x.join(timeout=10)
#       ftp_bounce(remotePath,device,picture)
# --------------------------------        
# preparo il topic (append)
        ptopic = "{}{}{}{}{}".format(FIWARE, ENTITY,"camera:", device,"/attrs")
        print("ptopic:",ptopic)  
# preparo il nuovo messaggio (JSON)
        ID = "{}{}{}".format(ENTITY,"camera:", device)
        EPOCH = round(time.time() * 1000)
        TS = strftime('%Y-%m-%d %H:%M:%S', localtime(EPOCH))
        payload = json.dumps({"id":ID,"timestamp":TS,"picture":picture})
        print( ">>>>>>>> MQTTS payload:",payload )
# pubblico il messaggio
        on_mqtts_publish(ptopic, payload)
# dopo non esegue nulla !

# -------------------------------------------------
def on_mqtts_message(client, userdata, result):
    message = str(result.payload.decode("utf-8"))
    print("---------vvvvvv  New Message on MQTTS !")
    print( "message:" + message )
    print("---------^^^^^^")
# Append-EVERY TOPICs to a file with the DEVICE name
    appendix = result.topic.split(":")[3]
    device = appendix[:-6]
    print("APPEND:" + device)
# ----------------------------------- APPEND MESSAGE 
    y = threading.Thread(target=mess_append, args=(device,message))
    y.start()
    #y.join(timeout=10)
# -------------------------------------------------
# connect to mqtt ARDESIA
def mqtt_connect(mqtt_username, mqtt_password, broker_endpoint, port):
    #global mqtt_client
    #global mqtt_connected

    if not mqtt_connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_publish = on_mqtt_publish
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()
        #mqtt_client.loop_forever()
        attempts = 0

        while not mqtt_connected and attempts < 5:  # Wait for connection
            print(mqtt_connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not mqtt_connected:
        print("[ERROR] Could not connect to broker")
        return False

    return True

# -------------------------------------------------
# conect a mqtts WeLASER
def mqtts_connect(mqtt_username, mqtt_password, broker_endpoint, port):
    #global mqtts_client
    #global mqtts_connected

    if not mqtts_connected:
        mqtts_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtts_client.on_connect = on_mqtts_connect
        mqtts_client.on_publish = on_mqtts_publish
        mqtts_client.on_message = on_mqtts_message
        mqtts_client.tls_set(ca_certs=None,
                            certfile=None,
                            keyfile=None,
                            cert_reqs=ssl.CERT_NONE, #<<<<<<<< MQTTS cert not Valid bypass
                            tls_version=ssl.PROTOCOL_TLSv1_2,
                            ciphers=None)
        mqtts_client.tls_insecure_set(True)           #<<<<<<<< MQTTS cert not Valid bypass
        mqtts_client.connect(broker_endpoint, port=port)
        mqtts_client.loop_start()
        #mqtts_client.loop_forever()
        attempts = 0

        while not mqtts_connected and attempts < 5:  # Wait for connection
            print(mqtts_connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not mqtts_connected:
        print("[ERROR] Could not connect to broker")
        return False
    return True

# -------------------------------------------------
# publish a MQTT
def mqtt_publish(client, topic, payload):
    try:
        client.publish(topic, payload)
    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))

# -------------------------------------------------
# subscribe a MQTT 
def mqtt_subscribe(client,topic):
    try:
# OVERLAY stopic -> SUBSCRIBE ALL
        client.subscribe(topic)
    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))

# ==========================================================
#                     FTP
# -------------------------------------------------
def retrieveFile(ftp, remotePath, localPath, fileName):
    localFile = os.path.join(localPath,  fileName)
    print("retrieving:" + localFile)
    file = open(localFile, 'wb')
    ftp.cwd(remotePath)
    ftp.retrbinary('RETR ' + fileName, file.write, 1024)
    file.close()

# -------------------------------------------------
def sendFile(ftp, remotePath, localPath, fileName):
    localFile = os.path.join(localPath,  fileName)
    print("sending:" + localFile)
    file = open(localFile, 'rb')
    ftp.cwd(remotePath)
    ftp.storbinary('STOR '+ fileName , file)
    file.close

# -------------------------------------------------
def ftp_bounce(remotePath,device,picture):
    print("THREAD <BOUNCE> LAUNCHED ",remotePath," <<<<<<<< ", picture)
    try:
        client_from = FTP()
        client_from.debugging = 5
        client_from.connect(host=HOST_FROM, port=PORT_FROM)
        client_from.login(user=USER_FROM,passwd=PASS_FROM)
        print("connected ftp 1")
        # --------------------
        client_to = FTP()
        client_to.debugging = 5
        client_to.connect(host=HOST_TO, port=PORT_TO)
        client_to.login(user=USER_TO,passwd=PASS_TO)
        print("connected ftp 2")
        #-------------------
        retrieveFile(client_from,remotePath,PATH_LOCAL,picture)
        sendFile(client_to,remotePath,PATH_LOCAL,picture)
        client_from.close()
        client_to.close()
        # es> check if fix works
        oldFile = os.path.join(PATH_LOCAL, picture)
        newFile = os.path.join(PATH_LOCAL, device + '.jpg')
        shutil.move(oldFile, newFile)
        #os.system("mv -f " + oldFile +" "+newFile)
        return True
    except all_errors as e:
        print( 'Error in Ftp -> ', e )
        return False
# ==========================================================
#                    APPEND
# -------------------------------------------------
def mess_append(device, message):
    print("THREAD <APPEND> LAUNCHED on device:",device)
    # NON FA IN TEMPO..ARRIVA UN ALTRO MESSAGGIO
    if (device != "test") :
        ''' # es> removed because managed by .env
        if os.name == "nt":
            PATH_LOCAL = "DATA/"'''
        # es>
        FNAME = os.path.join(PATH_LOCAL, device + '.txt')
        print("FNAME:" + FNAME)
        if not os.path.exists(FNAME):
            file1 = open(FNAME, "w")  # NEW write file
        else:
            file1 = open(FNAME, "a")  # append mode
        file1.write(message)
        file1.write("\n")
        file1.close()
        return True
# ==========================================================
def main():
# global mqtt_client
# global mqtts_client
    # mi connetto a 'MQTTS WeLASER
    mqtts_connect(MQTTS_USERNAME,MQTTS_PASSWORD, MQTTS_BROKER, MQTTS_PORT)
    # mi connetto a 'MQTT Ardesia
    mqtt_connect(MQTT_USERNAME,MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT)
    # pubblico il messaggio TEST su MQTTS
    ptopic = "{}{}{}".format(FIWARE, ENTITY,"device:test/attrs")
    print("ptopic=" + ptopic)
    ID = "{}{}".format(ENTITY,"device:test")
    EPOCH = round(time.time() * 1000)
    #TS = strftime('%Y-%m-%d %H:%M:%S', localtime(EPOCH))
    payload = json.dumps({"id":ID,
                        #"timestamp": TS,
                        "message": 'test'})
    mqtt_publish(mqtts_client, ptopic, payload)
    # mi iscrivo a MQTTS
    stopic = "{}{}".format(FIWARE, "+/attrs")
    print("WELASER stopic=" + stopic)
    mqtt_subscribe(mqtts_client, stopic)
    # mi iscrivo ad una certa classe di messaggi su MQTT
    stopic = "#"
    print("ARDESIA stopic=" + stopic)
    mqtt_subscribe(mqtt_client,stopic)  

# ---------------------------------------------------------
if __name__ == '__main__':
#while True:
    main()
    #time.sleep(60)