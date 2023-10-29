import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const dev_name = params.device
  try {
    // Find all Devices with name "x"
    /*
    const devicesToDelete = await prisma.device.findMany({
      where: {
        timestamp: {        
            lt: new Date('2023-01-01T13:14:32.000Z')
        },
      },
      include: {
        weatherStation: true, // Include the associated WeatherStation
        weatherStationStd: true,
        weatherStationVirtual: true
      },
    });
    // Iterate through each device and delete its associated WeatherStation
    for (const device of devicesToDelete) {
      if (device.weatherStation) {
        await prisma.weatherStation.delete({
          where: {
            id: device.weatherStation.id,
          },
        });
      }
      if (device.weatherStationStd) {
        await prisma.weatherStationStd.delete({
          where: {
            id: device.weatherStationStd.id,
          },
        });
      }
      if (device.weatherStationVirtual) {
        await prisma.weatherStationVirtual.delete({
          where: {
            id: device.weatherStationVirtual.id,
          },
        });
      }
    }
    */
    // Delete the Devices with old timestamp
    let toDelete = await prisma.device.deleteMany({
      where: {
        timestamp: {        
          lt: new Date('2023-01-01T13:14:32.000Z')
        },
      },
    });
    console.log(`Deleted ${toDelete} devices`); 

    toDelete = await prisma.weatherStation.deleteMany({
      where: {
        timestamp: {        
          lt: new Date('2023-01-01T13:14:32.000Z')
        },
      },
    });
    console.log(`Deleted ${toDelete} weatherStation`); 

    toDelete = await prisma.weatherStationStd.deleteMany({
      where: {
        timestamp: {        
          lt: new Date('2023-01-01T13:14:32.000Z')
        },
      },
    });
    console.log(`Deleted ${toDelete} weatherStationStd`); 

    return json(toDelete)
  } catch (error) {
    console.error('Error deleting WeatherStations and Devices:', error);
  }  
  
}