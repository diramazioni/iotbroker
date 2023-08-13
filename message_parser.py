import asyncio
from time import localtime, strftime
import traceback
from prisma import Prisma
import json
import logging


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
            e = payload
            TS = strftime("%Y-%m-%d %H:%M:%S", localtime(e["timestamp"]))
            sens = {}
            for se in e["value"]:
                sens[se["name"]] = dict(zip(se["controlledProperty"], se["value"]))
                units = dict(zip(se["controlledProperty"], se["units"]))
                for name, value in units.items():
                    units_db = await self.db.units.find_unique(where={"name": name})
                    if not units_db:
                        logging.info("U" * 80, name)
                        units_obj = {"name": name, "value": value, "type": e["name"]}
                        units_db = await self.db.units.create(units_obj)

            device_obj = {
                "name": e["name"],
                "timestamp": e["timestamp"],
            }
            if "calibration" in e:
                device_obj["calibration"] = e["calibration"]
            device_db = await self.db.device.create(device_obj)

            sens_obj = {
                "device": {
                    "connect": {
                        "id": device_db.id,
                    },
                },
                "timestamp": TS,
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
            elif "WeatherStation" in e["name"]:
                logging.info("-" * 80, sens_obj)
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
    # await sensor_processor.process_data("data/ETRometer_1.json")
    await message_parser.process_data("data/WeatherStation_n1.json")
    asyncio.sleep(10)
    await message_parser.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
