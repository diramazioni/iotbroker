import asyncio
from time import localtime, strftime
from prisma import Prisma
import json


class SensorProcessor:
    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        await self.db.connect()

    async def disconnect(self):
        await self.db.disconnect()

    async def db_entry(self, payload) -> None:
        e = payload
        TS = strftime("%Y-%m-%d %H:%M:%S", localtime(e["timestamp"]))
        sens = {}
        for se in e["value"]:
            sens[se["name"]] = dict(zip(se["controlledProperty"], se["value"]))
            units = dict(zip(se["controlledProperty"], se["units"]))
            for name, value in units.items():
                units_db = await self.db.units.find_unique(where={"name": name})
                if not units_db:
                    print("U" * 80, name)
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
            print(sensor_name)
            if "SCD30" in sensor_name:
                sens_obj["name"] = sensor_name
                sens_obj.update(d)
                print("-" * 80)
                print(sens_obj)
                await self.db.etrometer.create(sens_obj)
            else:
                sens_obj.update(d)
        if "ETRometer" in e["name"]:
            pass
        elif "WeatherStation" in e["name"]:
            print("-" * 80, sens_obj)
            await self.db.weatherstation.create(sens_obj)

    async def process_data(self, data_file) -> None:
        with open(data_file) as f:
            data_json = json.load(f)

            for e in data_json:
                await self.db_entry(e)


async def main() -> None:
    sensor_processor = SensorProcessor()
    await sensor_processor.connect()
    # await sensor_processor.process_data("data/ETRometer_1.json")
    await sensor_processor.process_data("data/WeatherStation_n1.json")
    await sensor_processor.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
