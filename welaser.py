"""
WELASER - by GV June 2023
Capture messages from  Ardesia MQTT (insecure)
and publish them to WeLASER MQTTS (over TLS)
then parse MQTT message, extract FTP file name and copy
the files from  Ardesia to Local and to WeLASER
Further on capture messages from MQTTS and
append them to device.txt
Finally publish a TEST message on MQTTS 
"""
import os
import sys

import paho.mqtt.client as mqttClient
import json

# import ast # to convert string into dictionary
import ssl
from ftplib import FTP, all_errors
import time
from time import strftime, localtime

# from datetime import datetime  # datetime data type

# from datetime import datetime  # datetime data type

from dotenv import load_dotenv  # legge codici di accesso
import shutil
import daemon
import argparse
import logging

"""
    handlers=[
        logging.FileHandler("welaser.log"),
        logging.StreamHandler()
    ]    #    
"""
#  ==========================================
#          LOADS ENVIROMENT VARIABLES
load_dotenv()
# MQTT at ardesia
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")  # Put here your Ubidots TOKEN
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")  # Leave this in blank
# MQTTS
# BROKER MQTTS at  "csi-traffic.campusfc.unibo.it"
MQTTS_BROKER = os.getenv("MQTTS_BROKER")
MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")
# FTPs
HOST_TO = os.getenv("HOST_TO")
PORT_TO = int(os.getenv("PORT_TO"))
USER_TO = os.getenv("USER_TO")
PASS_TO = os.getenv("PASS_TO")

HOST_FROM = os.getenv("HOST_FROM")
PORT_FROM = int(os.getenv("PORT_FROM"))
USER_FROM = os.getenv("USER_FROM")
PASS_FROM = os.getenv("PASS_FROM")

FTP_LOCAL = os.getenv("FTP_LOCAL")
FIWARE = os.getenv("FIWARE")
ENTITY = os.getenv("ENTITY")


PATH_LOCAL = os.getcwd()


#  ==========================================
#                global variables

mqtts_client = mqttClient.Client()
mqtt_client = mqttClient.Client()


#  ==========================================
#                   Functions
#  ==========================================
#                    MQTT(S)
# --------------------------------------------
def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("[INFO] Connected to MQTT broker - ARDESIA")
    else:
        logging.error("[INFO] Error, connection failed")


# -------------------------------------------------
def on_mqtts_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("[INFO] Connected to MQTTS broker - WeLASER")
    else:
        logging.error("[INFO] Error, connection failed")


# -------------------------------------------------
def on_mqtt_publish(client, userdata, result):
    logging.debug("MQTT Published!")


# -------------------------------------------------
def on_mqtts_publish(client, userdata, result):
    logging.debug("MQTTS Published!")


# -------------------------------------------------
def on_mqtt_message(client, userdata, result):
    # TODO: Giuliano perché devi fare queste sostituzioni???
    # str().replace(" ", "").replace("\'", "\"").replace('/n', '')
    message = result.payload.decode("utf-8")
    logging.info("---------vvvvvv ---- New Message on MQTT !")
    logging.debug("message:" + message)

    # PARSING - deserialising
    content = json.loads(message)
    device = content["nodeId"]
    device_name = message.topic.split(":")[-1].split("/")[0]
    logging.debug(f"device = nodeId:{device}")
    packetType = content["packetType"]
    logging.debug(f"packetType: {packetType}")
    if packetType == "picture":
        picture = content["data"]
        logging.debug(">>>>>>>>>>>>>> WITH PICTURE:" + picture)
        # ----------------------------------- INVIO FTP
        ftp_bounce(device_name, picture)
        ptopic = "{}{}{}{}{}".format(FIWARE, ENTITY, "camera:", device, "/attrs")
        logging.debug(f"ptopic:{ptopic}")
        # preparo il nuovo messaggio (JSON)
        ID = "{}{}{}".format(ENTITY, "camera:", device)
        TS = strftime("%Y-%m-%d %H:%M:%S", localtime(time.time()))
        payload = {"id": ID, "timestamp": TS, "picture": picture}
        logging.debug(f">>>>>>>> MQTTS payload:{payload}")
        mqtt_publish(mqtts_client, ptopic, json.dumps(payload))
        mess_append(device_name, payload)
        # pubblico il messaggio


# -------------------------------------------------
def on_mqtts_message(client, userdata, result):
    return True
    """ es> removing logging of all MQTTS messages
    message = result.payload.decode("utf-8")
    logging.info("---------vvvvvv  New Message on MQTTS !")
    logging.debug( "message:" + message )
    # Append-EVERY TOPICs to a file with the DEVICE name
    device = result.topic.split(":")[3][:-6]
    logging.info("APPEND:" + device)
    # ----------------------------------- APPEND MESSAGE
    mess_append(device, message)
    """


# -------------------------------------------------
# connect to mqtt ARDESIA
def mqtt_connect(mqtt_username, mqtt_password, broker_endpoint, port):
    mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_publish = on_mqtt_publish
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect(broker_endpoint, port=port)
    mqtt_client.loop_start()
    # mqtt_client.loop_forever()
    attempts = 0
    while not mqtt_client.is_connected() and attempts < 5:  # Wait for connection
        logging.debug("mqtt waiting to connect...")
        time.sleep(1)
        attempts += 1

    if not mqtt_client.is_connected():
        logging.debug("[ERROR] Could not connect to broker")
        return False

    return True


# -------------------------------------------------
# conect a mqtts WeLASER
def mqtts_connect(mqtt_username, mqtt_password, broker_endpoint, port):
    mqtts_client.username_pw_set(mqtt_username, password=mqtt_password)
    mqtts_client.on_connect = on_mqtts_connect
    mqtts_client.on_publish = on_mqtts_publish
    mqtts_client.on_message = on_mqtts_message
    mqtts_client.tls_set(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_NONE,  # <<<<<<<< MQTTS cert not Valid bypass
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )
    mqtts_client.tls_insecure_set(True)  # <<<<<<<< MQTTS cert not Valid bypass
    mqtts_client.connect(broker_endpoint, port=port)
    mqtts_client.loop_start()
    # mqtts_client.loop_forever()
    attempts = 0
    while not mqtts_client.is_connected() and attempts < 5:  # Wait for connection
        logging.debug("mqtts waiting to connect...")
        time.sleep(1)
        attempts += 1

    if not mqtts_client.is_connected():
        logging.error("[ERROR] Could not connect to broker")
        return False
    return True


# -------------------------------------------------
# publish to MQTT
def mqtt_publish(client, topic, payload):
    try:
        client.publish(topic, payload)
    except Exception as e:
        logging.error(f"[ERROR] Could not publish data: {e}")


# -------------------------------------------------
# subscribe to MQTT
def mqtt_subscribe(client, topic):
    try:
        # OVERLAY stopic -> SUBSCRIBE ALL
        client.subscribe(topic)
    except Exception as e:
        logging.error(f"[ERROR] Could not subscribe: {e}")


# ==========================================================
#                     FTP
# -------------------------------------------------
def retrieveFile(ftp, remotePath, fileName):
    localFile = os.path.join(PATH_LOCAL, fileName)
    logging.info("retrieving:" + localFile)
    with open(localFile, "wb") as file:
        ftp.cwd(remotePath)
        ftp.retrbinary("RETR " + fileName, file.write, 1024)
        file.close()


# -------------------------------------------------
def sendFile(ftp, remotePath, fileName):
    localFile = os.path.join(PATH_LOCAL, fileName)
    logging.info("sending:" + localFile)
    if os.path.exists(localFile):
        with open(localFile, "rb") as file:
            # file = open(localFile, 'rb')
            ftp.cwd(remotePath)
            ftp.storbinary("STOR " + fileName, file)
            file.close()
    else:
        logging.error("ftp file not found")


# -------------------------------------------------
def ftp_connect(host, port, user, password):
    try:
        client_ftp = FTP()
        client_ftp.debugging = 5
        client_ftp.connect(host=host, port=port)
        client_ftp.login(user=user, passwd=password)
        return client_ftp
    except all_errors as e:
        logging.error(f"Error in Ftp -> {host} \n{e}")


# -------------------------------------------------
def ftp_bounce(device, picture):
    # verifico chi produce l'immagine
    camType = device[0:5]  # camtype = [camer | robot]
    remotePath = ""
    PATH_ROBOT = "/robot_images"
    PATH_FIELD = "/field_images"
    if camType == "camer":
        remotePath = PATH_FIELD
    elif camType == "robot":
        remotePath = PATH_ROBOT

    try:
        client_from = ftp_connect(HOST_FROM, PORT_FROM, USER_FROM, PASS_FROM)
        logging.debug("connected ftp 1")
        retrieveFile(client_from, remotePath, picture)
        client_from.close()
        logging.debug("ftp 1 done")
    except all_errors as e:
        logging.error(f"Error in Ftp1 -> {e}")
        # --------------------
    try:
        client_to = ftp_connect(HOST_TO, PORT_TO, USER_TO, PASS_TO)
        logging.debug("connected ftp 2")
        # -------------------
        sendFile(client_to, remotePath, picture)
        client_to.close()
        logging.debug("ftp 2 done")
    except all_errors as e:
        logging.error(f"Error in Ftp2 -> {e}")
        return False
    # last step - copy the image to a local(www) file
    # ..with the name of camera (es. camera_5.jpg)
    #
    # es> check if fix works
    oldFile = os.path.join(PATH_LOCAL, picture)
    if os.path.exists(oldFile):
        logging.debug(f"mv {oldFile} picture to the www and dashboard")
        newFile = os.path.join(PATH_LOCAL, "data", device + ".jpg")
        shutil.copy(
            oldFile, os.path.join(PATH_LOCAL, "www", device + ".jpg")
        )  # server www
        shutil.move(oldFile, newFile)  # local copy
    else:
        logging.error(f"{oldFile} DOES NOT EXIST")
    return True


# ==========================================================
#                    APPEND
# -------------------------------------------------
def mess_append(device, message):
    try:
        message = json.loads(message)
        if device == "test":
            return True
        FNAME = os.path.join(PATH_LOCAL, "data", device + ".json")
        if not os.path.exists(FNAME):
            mes = []
        else:
            with open(FNAME) as f:
                mes = json.load(f)
        # append a new message to the list
        mes.append(message)
        with open(FNAME, "w") as f:
            f.write(json.dumps(mes))  # , indent=2
            f.close()
        # copy to the www server
        shutil.copy(FNAME, os.path.join(PATH_LOCAL, "www", device + ".json"))
        return True
    except all_errors as e:
        logging.error(f"Error in append -> {e}")


# =========================================================
def test_WELASER():
    print("=" * 80 + "\ntest_WELASER")
    ptopic = f"{FIWARE}{ENTITY}device:test/attrs"
    print("ptopic=" + ptopic)
    ID = f"{ENTITY}device:test"
    payload = json.dumps(
        {
            "name": "WeatherStation_nX",
            "id": "urn:ngsi-ld:Device:WeatherStation_nX",
            "value": [
                {
                    "name": "WeatherStation_nX_BAT",
                    "id": "urn:ngsi-ld:Device:WeatherStation_nX_BAT",
                    "controlledProperty": ["Battery_Voltage"],
                    "value": [4.130879741],
                    "units": ["volts"],
                },
                {
                    "name": "WeatherStation_nX_PV",
                    "id": "urn:ngsi-ld:Device:WeatherStation_nX_PV",
                    "controlledProperty": ["Solar_Panel_Voltage"],
                    "value": [0],
                    "units": ["volts"],
                },
                {
                    "name": "WeatherStation_nX_WIND",
                    "id": "urn:ngsi-ld:Device:WeatherStation_nX_WIND",
                    "controlledProperty": ["W_vel", "W_dir"],
                    "value": [88.63938536, 134.9650667],
                    "units": ["m/s", "deg-N-cw"],
                },
                {
                    "name": "WeatherStation_nX_BME680",
                    "id": "urn:ngsi-ld:Device:WeatherStation_nX_BME680",
                    "controlledProperty": [
                        "Temperature",
                        "Pressure",
                        "Humidity",
                        "GasResistance",
                        "Altitude",
                    ],
                    "value": [29.62742615, 1005.58, 50.22343063, 834.359, 103.4343262],
                    "units": ["degC", "hPa", "%", "KOhms", "m"],
                },
                {
                    "name": "WeatherStation_nX_SENTEK",
                    "id": "urn:ngsi-ld:Device:WeatherStation_nX_SENTEK",
                    "controlledProperty": [
                        "Ts_1",
                        "Ts_2",
                        "Ts_3",
                        "Us_1",
                        "Us_2",
                        "Us_3",
                    ],
                    "value": [
                        28.4299202,
                        28.02635002,
                        28.65796089,
                        0.000338,
                        0.004462,
                        0.002557,
                    ],
                    "units": ["degC", "degC", "degC", "%", "%", "%"],
                },
            ],
            "timestamp": 1690740135000,
        }
    )
    mqtt_publish(mqtts_client, ptopic, payload)


def test_ARDESIA():
    print("=" * 80 + "\ntest_ARDESIA")
    # send image to origin (ardesia) ftp for simulating camera real sending
    client_from = ftp_connect(HOST_FROM, PORT_FROM, USER_FROM, PASS_FROM)
    sendFile(client_from, PATH_FIELD, "test.jpg")
    client_from.close()

    # send to we
    test_img = "test.jpg"
    message = {"nodeId": "camera_36", "packetType": "picture", "data": test_img}
    ptopic = "WeLaser/PublicIntercomm/CameraToDashboard"
    payload = json.dumps(message)
    print(payload)
    mqtt_publish(mqtt_client, ptopic, payload)
    print("=" * 80 + "\nDONE")


def main():
    logging.debug("main()")
    # mi connetto a 'MQTTS WeLASER
    mqtts_connect(MQTTS_USERNAME, MQTTS_PASSWORD, MQTTS_BROKER, MQTTS_PORT)
    # mi connetto a 'MQTT Ardesia
    mqtt_connect(MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT)
    if not (mqtts_client.is_connected() and mqtt_client.is_connected()):
        logging.error("to many failed attempts to connects to mqtt/mqtts")
        sys.exit(1)
    # mi iscrivo a MQTTS
    stopic = f"{FIWARE}+/attrs"
    logging.debug("WELASER stopic=" + stopic)
    mqtt_subscribe(mqtts_client, stopic)
    # mi iscrivo ad una certa classe di messaggi su MQTT
    stopic = "#"
    logging.debug("ARDESIA stopic=" + stopic)
    mqtt_subscribe(mqtt_client, stopic)


# ---------------------------------------------------------
logging.basicConfig()
file_logger = logging.FileHandler("debug.log", "a")
formatter = logging.Formatter(
    fmt="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S "
)
file_logger.setFormatter(formatter)
file_logger.setLevel(logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(file_logger)
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--daemon", action="store_true", help="Run as a daemon")
    args = parser.parse_args()
    if args.daemon:
        print("running WeLaser Daemon")
        with daemon.DaemonContext(files_preserve=[file_logger.stream.fileno()]):
            logging.info(" ~ WELASER iotbroker DAEMON ~ ")
            try:
                main()
                while True:
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Error {e}")
            finally:
                sys.exit(1)
    else:
        try:
            main()
            in_ = ""
            while in_ not in ["x", "X"]:
                print("\/" * 10 + "    WAITING FOR INPUT    " + "\/" * 10)
                in_ = input(
                    '"x" to exit., \n"a" test ARDESIA \n"w" test WELASER \n"f" test ftp 1 e 2 connections\n'
                )
                print("\/" * 40)
                if in_ in ["a", "A"]:
                    test_ARDESIA()
                elif in_ in ["w", "W"]:
                    test_WELASER()
                elif in_ in ["f", "F"]:
                    print("test ftp connections")
                    client_from = ftp_connect(
                        HOST_FROM, PORT_FROM, USER_FROM, PASS_FROM
                    )
                    client_to = ftp_connect(HOST_TO, PORT_TO, USER_TO, PASS_TO)
        except Exception as e:
            logging.error(f"Error {e}")

        finally:
            mqtt_client.loop_stop()
            mqtts_client.loop_stop()

            sys.exit(1)
