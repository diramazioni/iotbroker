import asyncio
from time import localtime, strftime
import traceback
from prisma import Prisma
import json
import logging

'''
Seed the DB with saved json messages from the MQTT broker
Insert the MQTT messages into the DB
'''
class MessageParser:
    def __init__(self):
        self.db = Prisma()
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        logging.info("Connecting to DB")
        await self.db.connect()

    async def disconnect(self):
        logging.info("Disconnecting from DB")
        await self.db.disconnect()

    async def db_entry(self, payload) -> None:
        try:
            unames_ = dict()
            e = payload
            TS = strftime("%Y-%m-%d %H:%M:%S", localtime(e["timestamp"]))
            if ("Camera" in e["id"] or "camera" in e["id"]):
                logging.info(f"Camera: {e['id']}")
                camera_obj = {"timestamp": int(e['timestamp']), "picture": e['picture']}
                await self.db.camera.create(camera_obj)
                return
            
            sens = {}
            
            async def insert_units(device_name, unames={}):
                for name, value in unames.items():
                    if name not in unames_:
                        units_db = await self.db.units.find_unique(where={"name": name})
                        if not units_db:
                            logging.info(f"Update Units {name}")
                            units_obj = {"name": name, "value": value, "type": device_name}
                            units_db = await self.db.units.create(units_obj)
                            unames_[name] = units_obj
                        else:  # cache the results
                            units_obj = {"name": name, "value": value, "type": device_name}
                            unames_[name] = units_obj
                            
            if all(isinstance(item, (int, float)) for item in e["value"]):
                sens[e["name"]] = dict(zip(e["controlledProperty"], e["value"]))
                units = dict(zip(e["controlledProperty"], e["units"]))
                await insert_units(e["name"], units)
            elif all(isinstance(item, dict) for item in e["value"]):  # gerarchic structure
                for se in e["value"]:
                    sens[se["name"]] = dict(zip(se["controlledProperty"], se["value"]))
                    units = dict(zip(se["controlledProperty"], se["units"]))
                    await insert_units(e["name"], units)

            device_obj = {
                "name": e["name"],
                "timestamp": e["timestamp"],
            }
            if "calibration" in e:
                device_obj["calibration"] = bool(e["calibration"])
            if "areaServed" in e:
                device_obj["areaServed"] = e["areaServed"]
            if "location" in e:
                device_obj["location"] = str(e["location"]["coordinates"])
            device_db = await self.db.device.create(device_obj)

            sens_obj = {
                "device": {
                    "connect": {
                        "id": device_db.id,
                    },
                },
                "timestamp": e["timestamp"],
            }

            for sensor_name, d in sens.items():
                logging.info(sensor_name)
                if "SCD30" in sensor_name:
                    sens_obj["name"] = sensor_name
                    sens_obj.update(d)
                    logging.info("-" * 80)
                    logging.info(sens_obj)
                    await self.db.etrometer.create(sens_obj)
                else:
                    sens_obj.update(d)
            if "ETRometer" in e["name"]:
                pass
            elif "WeatherStation_v" in e["name"]:
                logging.info("-" * 80)
                logging.info(sens_obj)
                await self.db.weatherstationvirtual.create(sens_obj)
            elif "WeatherStation_n" in e["name"]:
                logging.info("-" * 80)
                logging.info(sens_obj)
                await self.db.weatherstation.create(sens_obj)
        except Exception as e:
            logging.error(f"db_entry error:{e}")  # Print the exception
            logging.error(traceback.format_exc())

    async def process_data(self, data_file) -> None:
        with open(data_file) as f:
            data_json = json.load(f)

            for e in data_json:
                await self.db_entry(e)


async def main() -> None:
    message_parser = MessageParser()
    await message_parser.connect()
    await message_parser.process_data("data/ETRometer_1.json")
    
    #await message_parser.process_data("data/WeatherStation_n1.json")
    await asyncio.sleep(10)
    await message_parser.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
