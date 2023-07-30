import asyncio
from time import localtime, strftime
from prisma import Prisma
import json, os

#async def process(payload) -> None:
    

async def main() -> None:
  db = Prisma()
  await db.connect()

  with open("data/ETRometer_2.json") as f:
    data_json = json.load(f)
    units = {}
    for e in data_json:
      #process(e)
      TS = strftime('%Y-%m-%d %H:%M:%S', localtime(e['timestamp']))
      sens = {}
      for se in e['value']:
        if ["battGauge"|"_BAT"] in se["name"]:
          batt = float(se["value"][0])
          units["charge"] = "volts"
        elif ["SCD30"|"PV"|"WIND"|"BME680"|"SENTEK"] in se["name"]:
          vals = se["value"]
          props = se["controlledProperty"]
          units_ = se["units"]
          units = units.update(dict(zip(props,units_)))
          sens[se["name"]] = dict(zip(props,vals))
        else:
          print(f"urecognized sensor {se['name']}")
          break

      device = await db.device.create({
        'name': e['name'],
        'calibration': e['calibration'],
        'timestamp': e['timestamp'],
        'charge':batt,
      })
      
      for sensor_name,d in sens.items():
        etr = {
          'device':{
            'connect': {
              'id': device.id,
            },
          }, 
          'timestamp':TS,                
          'name':sensor_name,
        }
        etr.update(d)
        print(sensor_name, etr)
        #break

        await db.etrometer.create(etr)       
    for name, value in units.items():
      await db.units.create({
        'name': name,
        'value': value,
      })        

    await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())