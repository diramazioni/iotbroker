import asyncio
from time import localtime, strftime
from prisma import Prisma
import json, os

db = Prisma()

async def db_entry(payload) -> None:
  e = payload
  TS = strftime('%Y-%m-%d %H:%M:%S', localtime(e['timestamp']))
  sens = {}
  for se in e['value']:
    units = dict(zip(se["controlledProperty"],se["units"]))
    sens[se["name"]] = dict(zip(se["controlledProperty"],se["value"]))
    for name, value in units.items():
      units_db = await db.units.find_unique(where={'name': name})
      if not units_db : 
        print("U"*80, name)
        units_obj = {       
          'name': name,
          'value': value,
          'type': e['name']
        }   
        units_db = await db.units.create(units_obj)
  device_obj = {
        'name': e['name'],
        'timestamp': e['timestamp'],
      }
  if 'calibration' in e : device_obj['calibration'] = e['calibration']
  device_db = await db.device.create(device_obj)

  sens_obj = {
    'device':{
      'connect': {
        'id': device_db.id,
      },
    }, 
    'timestamp':TS,                
  }
  for sensor_name,d in sens.items():
    if "ETRometer" in e["name"]: # necessario perché il nome del sensore è diverso per ogni sensore
      sens_obj['name'] = sensor_name  
    sens_obj.update(d)
  print("-"*80)
  if "ETRometer" in e["name"]:
    sens_db = await db.etrometer.create(sens_obj)
  elif "WeatherStation" in e["name"]:
    sens_db = await db.weatherstation.create(sens_obj)
  print(sens_obj)


  
async def main() -> None:

  await db.connect()
  with open("data/ETRometer_1.json") as f:
  #with open("data/WeatherStation_n1.json") as f:
    data_json = json.load(f)

    for e in data_json:
      await db_entry(e)

  await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())