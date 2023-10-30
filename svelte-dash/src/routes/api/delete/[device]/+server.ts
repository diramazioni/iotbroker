// /api/delete/WeatherStation_s1?start=2023-10-30T16:39:30.000Z&end=2023-10-30T16:42:30.000Z
import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const dev_name = params.device
	const startParam = url.searchParams.get('start');
	const endParam = url.searchParams.get('end');
	const where = {
		name: { 
			'equals': dev_name,
			mode: 'insensitive',
		},
	}
	if (startParam && endParam) {
		where['timestamp'] = {
			gte: startParam, // start
			lte: endParam  // end
		}
	}	
  try {
    // Find all Devices with name "x"
    const devicesToDelete = await prisma.device.findMany({
      where: where,
      include: {
        weatherStation: true, // Include the associated WeatherStation
        weatherStationStd: true,
        weatherStationVirtual: true
      },
    });
    console.log(`Deleted ${devicesToDelete.length} devices`); 
    
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
      await prisma.device.delete({
        where: {
          id: device.id,
        },
      });      
    }

    // // Delete the Devices with name "x"
    // await prisma.device.deleteMany({
    //   where: {
    //     name: dev_name,
    //   },
    // });
    
    return json(devicesToDelete)
  } catch (error) {
    console.error('Error deleting WeatherStations and Devices:', error);
  }  
  
}