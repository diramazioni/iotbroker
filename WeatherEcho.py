"""
WELASER - by GV July 2023
Capture MQTT messages from  WeLASER MQTTS
and append them locally with the name of topic.
Also access weather service, build a FIWARE
compliant message and publish it on WeLASER MQTTS
"""
import os
import threading
import paho.mqtt.client as mqttClient
import json
import ast  # to convert string into dictionary
import ssl
from ftplib import FTP
import time
from time import strftime, localtime
from datetime import datetime  # datetime data type

from dotenv import load_dotenv  # legge codici di accesso

from urllib.request import urlopen

#  ==========================================
#          LOADS ENVIROMENT VARIABLES
load_dotenv()

# BROKER MQTTS
MQTTS_BROKER = os.getenv("MQTTS_BROKER")
MQTTS_PORT = int(os.getenv("MQTTS_PORT"))
MQTTS_USERNAME = os.getenv("MQTTS_USERNAME")
MQTTS_PASSWORD = os.getenv("MQTTS_PASSWORD")

FIWARE = os.getenv("FIWARE")
ENTITY = os.getenv("ENTITY")

PATH_LOCAL = os.getenv("PATH_LOCAL")
#  ==========================================
#                global variable un

mqtts_connected = False  # Stores the connection status
device = ""
picture = ""
remotePath = ""

#  ==========================================
#                 WEATHER DATA
#  ==========================================
prefix = "https://api.openweathermap.org/data/2.5"
appid = "e85ec932235b56d4c778fe9d45e817b6"  # GV
# appid  = "82dbbc0ae53998f4fa25897ecc3670c2" # EM
" List of virtual-stations - vs "
vs_name = [
    "Arganda",
    "Ghilardino",
    "Fabbrico",
    "Cadriano",
    "CAAB",
    "OrtoBotanico",
    "Ozzano",
    "Tastrup",
    "Reusel",
]
vs_lon = [
    -3.481010,
    12.851667,
    10.809061,
    11.40969,
    11.405170,
    11.35339,
    11.47373,
    12.29216,
    5.17290,
]
vs_lat = [
    40.312878,
    43.686944,
    44.881420,
    44.54938,
    44.514330,
    44.50046,
    44.41341,
    55.65173,
    51.36600,
]
vs_area = [
    "6991ac61-8db8-4a32-8fef-c462e2369055",
    "001",
    "002",
    "003",
    "004",
    "005",
    "006",
    "006",
    "6991ac61-8db8-4a32-8fef-c462e2369055",
    "6991ac61-8db8-4a32-8fef-c462e2369055",
]


#  ==========================================
#                   Functions
#  ==========================================
#                    MQTTS
# --------------------------------------------
def on_mqtts_connect(client, userdata, flags, rc):
    global mqtts_connected  # Use global variable
    if rc == 0:
        print("[INFO] Connected to MQTTS broker - WeLASER")
        mqtts_connected = True  # Signal connection
    else:
        print("[INFO] Error, connection failed")


# -------------------------------------------------
def on_mqtts_publish(client, userdata, result):
    print("MQTTS Published!")


# -------------------------------------------------
def on_mqtts_message(client, userdata, result):
    message = str(result.payload.decode("utf-8"))
    print("---------vvvvvv  New Message on MQTTS !")
    print("message:" + message)
    print("---------^^^^^^")
    # Append-EVERY TOPICs to a file with the DEVICE name
    appendix = result.topic.split(":")[3]
    device = appendix[:-6]
    print("APPEND:" + device)
    # ----------------------------------- APPEND MESSAGE
    y = threading.Thread(
        target=mess_append,
        args=(
            device,
            message,
        ),
    )
    y.start()
    # y.join(timeout=10)


# -------------------------------------------------
# conect a mqtts WeLASER
def mqtts_connect(mqtts_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global mqtts_connected  # Use global variable
    if not mqtts_connected:
        print("connect mqtts")
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
def mqtt_subscribe(client, topic):
    try:
        # OVERLAY stopic -> SUBSCRIBE ALL
        client.subscribe(topic)
    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))


# ==========================================================
#                    APPEND
# -------------------------------------------------
def mess_append(device, message):
    print("THREAD <APPEND> LAUNCHED on device:", device)
    # NON FA IN TEMPO..ARRIVA UN ALTRO MESSAGGIO
    if device != "test":
        FNAME = PATH_LOCAL + "/" + device + ".txt"
        print("FNAME:" + FNAME)
        if not os.path.isfile(FNAME):
            file1 = open(FNAME, "w")  # NEW write file
        else:
            file1 = open(FNAME, "a")  # append mode
        file1.write(message)
        file1.write("\n")
        file1.close()
        return True


#  ====================================================
#               WEATHER DATA RETRIEVE
#  ====================================================
def retrieve_daily(i):
    keys = [
        "temp",
        "day",
        "min",
        "max",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_deg",
        "rain",
    ]
    vars = [
        "tc",
        "tc_avg",
        "tc_min",
        "tc_max",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_deg",
        "rain",
    ]
    meas = ["degC", "degC", "degC", "degC", "%", "mBar", "m/s", "degNcw", "mm"]

    vs_nam = vs_name[i]
    vs_loc = vs_locs[i]
    #
    # DOWNLOAD 7-Days DAILY DATA and SAVE
    # DAILY -  restituisce gli 8 dati giornalieri previsti a partire da quello del giorno corrente
    # 5 ore dopo la richiesta (es.7.45 -> 12.00) dt = epoch GMT
    rp = (
        prefix
        + "/onecall?"
        + vs_loc
        + "&exclude=current,minutely,hourly,alerts&appid="
        + appid
    )
    #
    print(rp)
    response = urlopen(rp)
    html_bytes = response.read()
    my_json = html_bytes.decode("utf-8")
    print(my_json)
    parsed = json.loads(my_json)
    # print(json.dumps(parsed, indent=4))
    hr = parsed["hourly"]
    dy = parsed["daily"]
    # print(dy)
    # n = range(len(dy))
    n = range(0, 1)  # prendo solo il primo dato
    for i in n:
        h = hr[i]
        print(i)
        # print(h)
        dt = h["dt"]
        # print(dt)

        epoch = h["dt"]
        datetime_obj = datetime.fromtimestamp(epoch)
        print("Local datetime:")
        print(datetime_obj)

        if k == "temp":
            temp = h[k]
            tc_avg = temp["day"] - 273.15
            tc_min = temp["min"] - 273.15
            tc_max = temp["max"] - 273.15
            print("tc_min:", tc_min)
            print("tc_max:", tc_max)
            print("tc_avg:", tc_avg)

        # >>>>>>>>>> AGGIORNAMENTO MODELLO SIMULAZIONE <<<<<<<
        # APPEND message to file
        # appendDaily(:)rc7 toFile:dataFile.

        # FIWARE epoch

        # FIWARE epoch
        epoch_micro = epoch * 1000  # in microsec
        tc = tk_avg - 273.15
        print("tc:", tc)

        # data_dict = {'tc':tc, "rh":rh, "pr":pr, "ws":ws, "wd":wd, "mm":mm}
        variables = {"tc", "rh", "pr", "ws", "wd", "mm"}
        values = {tc, rh, pr, ws, wd, mm}
        units = {"°C", "%", "mBar", "m/s", "°Ncw", "mm"}
        # json_data = json.dumps(data_dict)

        # >>>>>>>>>> AGGIORNAMENTO MODELLO SIMULAZIONE <<<<<<<
        # APPEND message to file
        # appendHourly(:)rc7 toFile:dataFile.
        return epoch_micro, variables, values, units


#  =============================================================
def retrieve_hourly(i):
    keys = ["temp", "humidity", "pressure", "wind_speed", "wind_deg", "rain"]
    vars = ["temperature", "humidity", "pressure", "wind_speed", "wind_deg", "rain"]
    meas = ["degC", "%", "mBar", "m/s", "degNcw", "mm"]

    vs_loc = "lat=" + str(vs_lat[i]) + "&lon=" + str(vs_lon[i])
    # vs_loc  =  "lat=40.3125&lon=3.480833"

    #
    # HOURLY -restituisce i 48 dati orari che includono il valore (osservato) all'ora precedente
    # a quella della richiesta (es.7.45 -> 7.00) dt = epoch GMT
    rp = (
        prefix
        + "/onecall?"
        + vs_loc
        + "&exclude=current,minutely,daily,alerts&appid="
        + appid
    )
    #
    print(rp)
    response = urlopen(rp)
    html_bytes = response.read()
    my_json = html_bytes.decode("utf-8")
    # print(my_json)
    parsed = json.loads(my_json)
    # print(json.dumps(parsed, indent=4))
    hr = parsed["hourly"]
    # print(hr)
    # n = range(len(hr))
    n = range(0, 1)  # prendo solo il primo dato
    for i in n:
        h = hr[i]
        print(i)
        # print(h)
        epoch = h["dt"]
        # timezone_offset = h["timezone_offset"]
        # datetime_obj=datetime.fromtimestamp(epoch)
        # print("Local datetime:")
        # print(datetime_obj)
        epoch_micro = epoch * 1000   # FIWARE epoch in microsec

        props = []
        value = []
        units = []
        nk = range(0, len(keys))
        for ik in nk:
            k = keys[ik]
            if k in h:
                val = h[k]
                if k == "temp":
                    val = h[k] - 273.15
                if k == "rain":
                    r = h[k]
                    val = r["1h"]
            else:
                if k == "rain":
                    val = 0
                else:
                    val = -999
            # print(val)
            # print(k,":",str(round(val, 3)))
            # data_dict = {'tc':tc, "rh":rh, "pr":pr, "ws":ws, "wd":wd, "mm":mm}
            props.append(vars[ik])
            value.append(round(val, 3))
            units.append(meas[ik])
        # json_data = json.dumps(data_dict)

    # >>>>>>>>>> AGGIORNAMENTO MODELLO SIMULAZIONE <<<<<<<
    # APPEND message to file
    # appendHourly(:)rc7 toFile:dataFile.
    return epoch_micro, props, value, units


# ==========================================================
def main(mqtts_client):
    "aggiornamento HOURLY"
    # delay = 900  # 15min
    delay = 3600  # 1h

    # mi connetto a 'MQTTS WeLASER
    
    if not mqtts_connect(
        mqtts_client, MQTTS_USERNAME, MQTTS_PASSWORD, MQTTS_BROKER, MQTTS_PORT
    ):
        return False

    # SUBSCRIBE (for reading & storing)
    stopic = "{}{}".format(FIWARE, "+/attrs")
    print("stopic=" + stopic)
    mqtt_subscribe(mqtts_client, stopic)
    # define data location (window mode) to class variable <data>
    # (OSProcess isWindows)
    #         ifTrue:[data := 'C:\Users\GV\Documents\DATA\Weather\OpenWeather\']
    #         ifFalse:[data := '/home/www/html/home/virtual-meteo/data/'].
    n_stations = len(vs_name)
    n = range(0, n_stations)
    while True:
        for i in n:
            result = retrieve_hourly(i)
            # pubblico il messaggio su MQTTS
            lon = round(vs_lon[i], 7)  #  3.480833
            lat = round(vs_lat[i], 7)  # 40.312500
            device = "WeatherStation_v" + str(i)
            ptopic = "{}{}{}{}{}".format(FIWARE, ENTITY, "Device:", device, "/attrs")
            print("ptopic=" + ptopic)
            ID = "{}{}{}".format(ENTITY, "Device:", device)
            payload = json.dumps(
                {
                    "id": ID,
                    "name": device,
                    "areaServed": ("urn:ngsi-ld:AgriFarm:" + vs_area[i]),
                    "location": {"coordinates": [lon, lat], "type": "Point"},
                    "timestamp": result[0],
                    "controlledProperty": result[1],
                    "value": result[2],
                    "units": result[3],
                }
            )

            print(payload)
            #mqtt_publish(mqtts_client, ptopic, payload)

        time.sleep(delay)


# ---------------------------------------------------------
if __name__ == "__main__":
    mqtts_client = mqttClient.Client(client_id="WeatherEcho")
    main(mqtts_client)
