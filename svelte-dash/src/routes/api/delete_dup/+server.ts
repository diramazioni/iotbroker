import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const device_selected = 'WeatherStation_v2'
  try {
    // Fetch all the devices
    const device_allTimestamp = await prisma.device.findMany({
      select: {timestamp: true, id:true },
      orderBy:  { timestamp: 'asc' } 
    });

    const devicesWithDuplicateTimestamps = await prisma.device.groupBy({
      by: ["name", "timestamp"],
      _count: {
        timestamp: true
      },
      having: {
        timestamp: {
          _count: {
              gt: 1,
          },            
        },
      },     
    });

    const distinctDevice = await prisma.device.findMany({
      distinct: ["name", "timestamp"],

      select: {
        id: true, name: true, timestamp: true
      },   
    });

    const duplicates = device_allTimestamp.filter((item, index, array) => {
      return array.findIndex(obj => obj.timestamp === item.timestamp) !== index;
    });
    console.log(distinctDevice.length)
    console.log(device_allTimestamp.length)
    return json(distinctDevice)
  } catch (error) {
    console.error('Error deleting WeatherStations and Devices:', error);
  }  
  
}