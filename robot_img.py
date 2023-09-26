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
import json
import os

import ssl
from ftplib import FTP, all_errors
import time
from time import strftime, localtime

import glob
from dotenv import load_dotenv  # legge codici di accesso
import shutil
import paho.mqtt.client as mqttClient

#  ==========================================
#          LOADS ENVIROMENT VARIABLES
load_dotenv()

HOST_TO = os.getenv("HOST_TO")
PORT_TO = int(os.getenv("PORT_TO"))
USER_TO = os.getenv("USER_TO")
PASS_TO = os.getenv("PASS_TO")

HOST_FROM = os.getenv("HOST_FROM")
PORT_FROM = int(os.getenv("PORT_FROM"))
USER_FROM = os.getenv("USER_FROM")
PASS_FROM = os.getenv("PASS_FROM")

MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID")
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

PATH_LOCAL = os.getenv("ROBOT_LOCAL")
PATH_REMOTE = os.getenv("ROBOT_REMOTE")
ARDESIA_TOPIC = os.getenv("ARDESIA_TOPIC")

# ==========================================================
#                     FTP


def sendFile(ftp, remotePath, fileName):
    localFile = os.path.join(PATH_LOCAL, fileName)
    print("sending:" + localFile)
    if os.path.exists(localFile):
        with open(localFile, "rb") as file:
            # file = open(localFile, 'rb')
            ftp.cwd(remotePath)
            ftp.storbinary("STOR " + fileName, file)
            file.close()
    else:
        print("ftp file not found")


# -------------------------------------------------
def ftp_connect(host, port, user, password):
    try:
        client_ftp = FTP()
        client_ftp.debugging = 5
        client_ftp.connect(host=host, port=port)
        client_ftp.login(user=user, passwd=password)
        return client_ftp
    except all_errors as e:
        print("Error in Ftp ->" + host + "\n", e)


# ==========================================================
#                        MQTT


def mqtt_connect(client_id, mqtt_username, mqtt_password, broker_endpoint, port):
    mqtt_client = mqttClient.Client(client_id=client_id)
    mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
    mqtt_client.connect(broker_endpoint, port=port)
    mqtt_client.loop_start()
    # mqtt_client.loop_forever()
    attempts = 0
    while not mqtt_client.is_connected() and attempts < 5:  # Wait for connection
        print("mqtt waiting to connect...")
        time.sleep(1)
        attempts += 1

    if not mqtt_client.is_connected():
        print("[ERROR] Could not connect to broker")
        return None

    return mqtt_client


def mqtt_publish(client, topic, payload):
    try:
        client.publish(topic, payload)
    except Exception as e:
        print("[ERROR] Could not publish data:", e)


# ==========================================================


def read_images(directory):
    image_list_f = glob.glob(os.path.join(directory, "*.jpg"))
    image_list = [os.path.basename(f) for f in image_list_f]
    return image_list


def ftp_Ardesia(image_list):
    try:
        client_to = ftp_connect(HOST_FROM, PORT_FROM, USER_FROM, PASS_FROM)
        print("connected ftp Ardesia")
        for picture in image_list:
            sendFile(client_to, PATH_REMOTE, picture)
        print("ftp done")
    except all_errors as e:
        print("Error in Ftp Ardesia ->", e)
    finally:
        client_to.close
        sendFile(client_to, PATH_REMOTE, picture)
        print("ftp Ardesia done")


def ftp_Cesena(image_list):
    try:
        client_to = ftp_connect(HOST_TO, PORT_TO, USER_TO, PASS_TO)
        print("connected ftp Cesena")
        for picture in image_list:
            sendFile(client_to, PATH_REMOTE, picture)
        print("ftp done")
    except all_errors as e:
        print("Error in Ftp Cesena ->", e)
    finally:
        client_to.close
        sendFile(client_to, PATH_REMOTE, picture)
        print("ftp Cesena done")


def publish_Ardesia(image_list):
    print("publish_Ardesia")
    mqtt_client = mqtt_connect(
        MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT
    )
    time.sleep(2)
    for picture in image_list:
        message = {
            "nodeId": picture[picture.find("robot_"):picture.find(".jpg")],
            "packetType": "picture",
            "data": picture,
        }
        mqtt_publish(mqtt_client, ARDESIA_TOPIC, json.dumps(message))
    time.sleep(1)

def moveToBackuo(image_list):
    # move into backup
    backup_dir = os.path.join(PATH_LOCAL, "backup")  # backup dir
    for picture in image_list:
        pictureFull = os.path.join(PATH_LOCAL, picture) 
        if os.path.exists(pictureFull):
            newFile = os.path.join(backup_dir, picture)
            print("move into backup " + newFile)
            shutil.move(pictureFull, newFile)  # local copy
        else:
            print(pictureFull + " DOES NOT EXIST")


def main():
    image_list = read_images(PATH_LOCAL)
    if len(image_list):
        ftp_Ardesia(image_list)
        publish_Ardesia(image_list)
        time.sleep(1)
        # ftp_Cesena(image_list)
        moveToBackuo(image_list)
        print("FINISH")


if __name__ == "__main__":
    main()
