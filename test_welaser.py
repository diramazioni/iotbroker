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

import ssl
from ftplib import FTP, all_errors
import time
from time import strftime, localtime

from dotenv import load_dotenv  # legge codici di accesso
import shutil
import daemon
import argparse
import logging

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
ATTRS = "/attrs"

PATH_LOCAL = os.getcwd()

mqtts_client = mqttClient.Client()
mqtt_client = mqttClient.Client()


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
    message = result.payload.decode("utf-8")
    logging.info(f"MQTT {message}")


# -------------------------------------------------
def on_mqtts_message(client, userdata, result):
    message = result.payload.decode("utf-8")
    logging.info(f"MQTTS {message}")


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
def test_WeatherStation():
    print("=" * 80 + "\ntest_WeatherStation")
    device = "Device:WeatherStation_n_test"
    ptopic = f"{FIWARE}{ENTITY}{device}{ATTRS}"
    print("ptopic=" + ptopic)
    ID = f"{ENTITY}{device}"
    payload = json.dumps(
        {
            "name": "WeatherStation_n_test",
            "id": "urn:ngsi-ld:Device:WeatherStation_n_test",
            "value": [
                {
                    "name": "WeatherStation_n_test_BAT",
                    "id": "urn:ngsi-ld:Device:WeatherStation_n_test_BAT",
                    "controlledProperty": ["Battery_Voltage"],
                    "value": [4.130879741],
                    "units": ["volts"],
                },
                {
                    "name": "WeatherStation_n_test_PV",
                    "id": "urn:ngsi-ld:Device:WeatherStation_n_test_PV",
                    "controlledProperty": ["Solar_Panel_Voltage"],
                    "value": [0],
                    "units": ["volts"],
                },
                {
                    "name": "WeatherStation_n_test_WIND",
                    "id": "urn:ngsi-ld:Device:WeatherStation_n_test_WIND",
                    "controlledProperty": ["W_vel", "W_dir"],
                    "value": [88.63938536, 134.9650667],
                    "units": ["m/s", "deg-N-cw"],
                },
                {
                    "name": "WeatherStation_n_test_BME680",
                    "id": "urn:ngsi-ld:Device:WeatherStation_n_test_BME680",
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
                    "name": "WeatherStation_n_test_SENTEK",
                    "id": "urn:ngsi-ld:Device:WeatherStation_n_test_SENTEK",
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


def test_WeatherStationVirtual():
    print("=" * 80 + "\ntest_WeatherStationVirtual")
    device = "Device:WeatherStation_v_test"
    ptopic = f"{FIWARE}{ENTITY}{device}{ATTRS}"
    print("ptopic=" + ptopic)
    ID = f"{ENTITY}{device}"
    payload = json.dumps(
        {
            "id": ID,
            "name": "WeatherStation_v_test",
            "areaServed": "urn:ngsi-ld:AgriFarm:007",
            "location": {
                "coordinates": [5.1729, 51.366],
                "type": "Point",
            },
            "timestamp": 1691600400000,
            "controlledProperty": [
                "temperature",
                "humidity",
                "pressure",
                "wind_speed",
                "wind_deg",
                "rain",
            ],
            "value": [19.79, 61, 1018, 4.55, 300, 0],
            "units": ["degC", "%", "mBar", "m/s", "degNcw", "mm"],
        }
    )
    mqtt_publish(mqtts_client, ptopic, payload)


def test_ETRometer():
    print("=" * 80 + "\ntest_ETRometer")
    device = "Device:ETRometer_test"
    ptopic = f"{FIWARE}{ENTITY}{device}{ATTRS}"
    print("ptopic=" + ptopic)
    ID = f"{ENTITY}{device}"
    payload = json.dumps(
        {
            "name": "ETRometer_test",
            "id": "urn:ngsi-ld:Device:ETRometer_test",
            "wlan": "WeLaserAP",
            "value": [
                {
                    "id": "urn:ngsi-ld:Device:ETRometer_test_battGauge/attrs",
                    "name": "ETRometer_test_battGauge",
                    "controlledProperty": ["charge"],
                    "units": ["volts"],
                    "value": [-1],
                },
                {
                    "id": "urn:ngsi-ld:Device:ETRometer_test_SCD30-0",
                    "name": "ETRometer_test_SCD30-0",
                    "controlledProperty": ["CO2", "TC", "RH"],
                    "value": [542.97, 32, 39.5],
                    "units": ["ppm", "degC", "%"],
                },
                {
                    "id": "urn:ngsi-ld:Device:ETRometer_test_SCD30-1",
                    "name": "ETRometer_test_SCD30-1",
                    "controlledProperty": ["CO2", "TC", "RH"],
                    "value": [461.01, 32.15, 39.13],
                    "units": ["ppm", "degC", "%"],
                },
                {
                    "id": "urn:ngsi-ld:Device:ETRometer_test_SCD30-2",
                    "name": "ETRometer_test_SCD30-2",
                    "controlledProperty": ["CO2", "TC", "RH"],
                    "value": [490.27, 32.24, 39.03],
                    "units": ["ppm", "degC", "%"],
                },
            ],
            "calibration": "false",
            "timestamp": 1690740040000,
        }
    )
    mqtt_publish(mqtts_client, ptopic, payload)


def test_Canera():
    device = "Device:camera_test"
    ptopic = f"{FIWARE}{ENTITY}{device}{ATTRS}"
    ID = f"{ENTITY}{device}"
    TS = time.time()
    picture = "test.jpg"
    payload = json.dumps(
        {"id": ID, "name": "Camera_Test", "timestamp": TS, "picture": picture}
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
    mqtts_connect(MQTTS_USERNAME, MQTTS_PASSWORD, MQTTS_BROKER, MQTTS_PORT)
    mqtt_connect(MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT)
    if not (mqtts_client.is_connected() and mqtt_client.is_connected()):
        logging.error("to many failed attempts to connects to mqtt/mqtts")
        sys.exit(1)
    stopic = f"{FIWARE}+/attrs"
    logging.debug("WELASER stopic=" + stopic)
    mqtt_subscribe(mqtts_client, stopic)
    stopic = "#"
    logging.debug("ARDESIA stopic=" + stopic)
    mqtt_subscribe(mqtt_client, stopic)


# ---------------------------------------------------------
logging.basicConfig()

if __name__ == "__main__":
    try:
        main()
        in_ = ""
        while in_ not in ["x", "X"]:
            print("\/" * 10 + "    WAITING FOR INPUT    " + "\/" * 10)
            in_ = input(
                '\
                    "x" to exit., \n\
                    "1" test_Canera \n\
                    "2" test_WeatherStation \n\
                    "3" test_WeatherStationVirtual\n\
                    "4" test_ETRometer\n\
                    "5" test ftp\n'
            )
            print("\/" * 40)
            if in_ in ["1"]:
                test_Canera()
            elif in_ in ["2"]:
                test_WeatherStation()
            elif in_ in ["3"]:
                test_WeatherStationVirtual()
            elif in_ in ["4"]:
                test_ETRometer()
            elif in_ in ["5"]:
                print("test ftp connections")
                client_from = ftp_connect(HOST_FROM, PORT_FROM, USER_FROM, PASS_FROM)
                client_to = ftp_connect(HOST_TO, PORT_TO, USER_TO, PASS_TO)
            elif in_ in ["x", "X"]:
                sys.exit(0)
    except Exception as e:
        logging.error(f"Error {e}")

    finally:
        mqtt_client.loop_stop()
        mqtts_client.loop_stop()

        