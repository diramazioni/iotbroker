import asyncio
from time import localtime, strftime
from datetime import datetime
import traceback
from prisma import Prisma
import json
import logging

#from prisma.models import DateTime

"""
Seed the DB with saved json messages from the MQTT broker
Insert the MQTT messages into the DB
"""


class MessageParser:
    def __init__(self):
        self.db = Prisma()
        self.logger = logging.getLogger(__name__)
        self.units = {}
        

    async def connect(self):
        logging.info("Connecting to DB")
        await self.db.connect()

    async def disconnect(self):
        logging.info("Disconnecting from DB")
        await self.db.disconnect()

    async def db_entry(self, payload) -> None:
        try:
            e = payload
            if "Camera" in e["id"] or "camera" in e["id"]:
                device_type = "Camera"
            elif "ETRometer" in e["name"]:
                device_type = "ETRometer"
            elif "WeatherStation_v" in e["name"]:
                device_type = "WeatherStation_v"
            elif "WeatherStation_n" in e["name"]:
                device_type = "WeatherStation_n"
            elif "WeatherStation_s" in e["name"]:
                device_type = "WeatherStation_s"
            logging.info("-" * 80)
            logging.info(device_type)

            sens = {}
            timestamp = datetime.utcfromtimestamp(int(e["timestamp"]/1000))  # .isoformat()
            logging.debug(f"Timestamp: {timestamp}")
            
            # Camera message: insert directly ino the db
            if device_type == "Camera":
                logging.info(f"Camera: {e['id']}")
                camera_obj = {"timestamp": timestamp, "picture": e["picture"]}
                await self.db.camera.create(camera_obj)
                return

            # Cache the Units table
            if not self.units:
                units_db = await self.db.units.find_many()
                logging.info("*" * 80)
                for u in units_db:
                    self.units[(u.type, u.name)] = u.value
                logging.info(self.units)
                
            # Create the units if they don't exist
            async def insert_units(device_type, unames={}):
                for name, value in unames.items():
                    if (device_type, name) not in self.units:
                        # units_db = await self.db.units.find_unique(where={"name": name})
                        units_obj = {
                            "name": name,
                            "value": value,
                            "type": device_type,
                        }
                        units_db = await self.db.units.create(units_obj)
                        self.units[(device_type, name)] = value
                    else:
                        logging.debug("skipping " + name)
            if all(isinstance(item, (int, float)) for item in e["value"]):
                sens[e["name"]] = dict(zip(e["controlledProperty"], e["value"]))
                units = dict(zip(e["controlledProperty"], e["units"]))
                await insert_units(device_type, units)
            elif all(isinstance(item, dict) for item in e["value"]):  # tree structure
                for se in e["value"]:
                    sens[se["name"]] = dict(zip(se["controlledProperty"], se["value"]))
                    units = dict(zip(se["controlledProperty"], se["units"]))
                    await insert_units(device_type, units)

            device_obj = {
                "name": e["name"],
                "timestamp": timestamp,
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
                "timestamp": timestamp,
            }
            
            for sensor_name, d in sens.items():
                logging.info(sensor_name)
                if "SCD30" in sensor_name:  # ETRometer
                    sens_obj["name"] = sensor_name
                    sens_obj.update(d)                    
                else:  # Other devices
                    sens_obj.update(d)
                    
            if device_type == "ETRometer":
                await self.db.etrometer.create(sens_obj)
            elif device_type == "WeatherStation_v":
                await self.db.weatherstationvirtual.create(sens_obj)
            elif device_type == "WeatherStation_n":
                await self.db.weatherstation.create(sens_obj)
            elif device_type == "WeatherStation_s":
                await self.db.weatherstationstd.create(sens_obj)
                
            logging.info("-" * 80)
            logging.info(sens_obj)
            
        except Exception as e:
            logging.error(f"db_entry error:{e}")  # Print the exception
            logging.error(traceback.format_exc())
            # import sys
            # sys.exit(1)

    async def process_data(self, data_file) -> None:
        with open(data_file) as f:
            data_json = json.load(f)

            for e in data_json:
                await self.db_entry(e)
                await asyncio.sleep(0.1)


async def main() -> None:
    message_parser = MessageParser()
    await message_parser.connect()
    # await message_parser.process_data("data/ETRometer_2.json")
    import glob 
    loop = asyncio.get_event_loop()
    background_tasks = set()
    for f in glob.glob("data/test/*.json"):
        print(f"Processing {f}")
        await asyncio.sleep(1)
        task = loop.create_task(message_parser.process_data(f))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        # await message_parser.process_data(f)
    await asyncio.wait(background_tasks)
    await asyncio.sleep(1)
    await message_parser.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
