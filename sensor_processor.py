from time import localtime, strftime
from prisma import Prisma
import json


class SensorProcessor:
    def __init__(self):
        self.db = Prisma()

    def connect(self):
        self.db.connect()

    def disconnect(self):
        self.db.disconnect()

    def db_entry(self, payload) -> None:
        e = payload
        TS = strftime("%Y-%m-%d %H:%M:%S", localtime(e["timestamp"]))
        sens = {}
        for se in e["value"]:
            sens[se["name"]] = dict(zip(se["controlledProperty"], se["value"]))
            units = dict(zip(se["controlledProperty"], se["units"]))
            for name, value in units.items():
                units_db = self.db.units.find_unique(where={"name": name})
                if not units_db:
                    print("U" * 80, name)
                    units_obj = {"name": name, "value": value, "type": e["name"]}
                    units_db = self.db.units.create(units_obj)

        device_obj = {
            "name": e["name"],
            "timestamp": e["timestamp"],
        }
        if "calibration" in e:
            device_obj["calibration"] = e["calibration"]
        device_db = self.db.device.create(device_obj)

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
                self.db.etrometer.create(sens_obj)
            else:
                sens_obj.update(d)
        if "ETRometer" in e["name"]:
            pass
        elif "WeatherStation" in e["name"]:
            print("-" * 80, sens_obj)
            self.db.weatherstation.create(sens_obj)

    def process_data(self, data_file) -> None:
        with open(data_file) as f:
            data_json = json.load(f)

            for e in data_json:
                self.db_entry(e)


def main() -> None:
    sensor_processor = SensorProcessor()
    sensor_processor.connect()
    # sensor_processor.process_data("data/ETRometer_1.json")
    sensor_processor.process_data("data/WeatherStation_n1.json")
    sensor_processor.disconnect()


if __name__ == "__main__":
    main()
