import logging
import os
import time

from dotenv import load_dotenv
import asyncio

# import aiohttp
from aiohttp import ClientSession

import json

from mqtt_logger import MessageLogger


class AsyncHttpClient:
    def __init__(self):
        pass

    async def fetch(self, url):
        async with ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()


class WeatherLogger(MessageLogger, AsyncHttpClient):
    def __init__(
        self, delay=3600, conf=None, fiware=None, entity=None, log_json=False
    ) -> None:
        super().__init__(log_json=log_json)

        self.delay = delay
        self.conf = self.load_conf(conf)
        self.FIWARE = fiware
        self.ENTITY = entity

    def load_conf(self, conf_file):
        with open(conf_file) as f:
            conf = json.load(f)
            f.close()
        return conf

    async def retrieve(self, i):
        c = self.conf
        # {c[""][i]}
        vs_loc = f'lat={c["vs_lat"][i]}&lon={c["vs_lon"][i]}'
        postfix = "&exclude=current,minutely,daily,alerts&appid="
        url = f'{c["prefix"]}/onecall?{vs_loc}{postfix}{c["appid"]}'

        response = await self.fetch(url)
        response = json.loads(response)
        hr = response["hourly"][0]  # prendo il primo (non il secondo)
        ts = (
            hr["dt"] * 1000
        )  # TODO; Giuliano perché in microsec??? devo riconvertirlo dopo
        values = []
        for key in c["keys"]:
            value = None
            if key in hr:
                value = hr[key]
                if key == "temp":
                    value -= 273.15
                elif key == "rain":
                    value = value["1h"]
            elif key == "rain":
                value = 0
            else:
                logging.error(
                    f"Key not found {key}"
                )  # TODO; Verifare la questione della pioggia
            values.append(value)
        return {
            "timestamp": ts,
            "controlledProperty": c["vars"],
            "value": values,
            "units": c["units"],
        }

    async def run(self):
        while True:
            c = self.conf
            for i, ws_name in enumerate(c["vs_name"]):
                logging.info(f"Retrieving weather data for {ws_name}")
                result = await self.retrieve(i)
                # raise Exception()
                lat_lon = [round(c["vs_lon"][i], 7), round(c["vs_lat"][i], 7)]
                device = f"WeatherStation_v{i}"
                dev_ = "Device:"
                ptopic = f"{self.FIWARE}{self.ENTITY}{dev_}{device}/attrs"
                id = f"{self.ENTITY}{dev_}{device}"
                payload = {
                    "id": id,
                    "name": device,
                    "areaServed": ("urn:ngsi-ld:AgriFarm:" + c["vs_area"][i]),
                    "location": {"coordinates": lat_lon, "type": "Point"},
                }
                payload.update(result)
                logging.debug(json.dumps(payload, indent=2))
                await self.publish(ptopic, payload)
            #await asyncio.sleep(self.delay)


async def main(interactive=False):
    load_dotenv()
    FIWARE = os.getenv("FIWARE")
    ATTRS = os.getenv("ATTRS")
    ENTITY = os.getenv("ENTITY")

    weatherLogger = WeatherLogger(
        delay=3600,
        conf="openweathermap_conf.json",
        fiware=FIWARE,
        entity=ENTITY,
        log_json=True,
    )

    await weatherLogger.listen(
        host=os.getenv("MQTTS_BROKER"),
        port=int(os.getenv("MQTTS_PORT")),
        username=os.getenv("MQTTS_USERNAME"),
        password=os.getenv("MQTTS_PASSWORD"),
        tls=True,
        tls_insecure=True,
        notify_birth=True,
    )
    await weatherLogger.run()

    if interactive:
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(interactive=True))
