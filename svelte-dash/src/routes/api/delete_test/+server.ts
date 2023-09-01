import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const dev_name = 'WeatherStation_n_test'
  try {
    // Find all Devices with name "x"
    const devicesToDelete = await prisma.device.findMany({
      where: {
        name: dev_name,
      },
      include: {
        weatherStation: true, // Include the associated WeatherStation
      },
    });
    console.log(`Deleted ${devicesToDelete.count} devices`); 
    // Iterate through each device and delete its associated WeatherStation
    for (const device of devicesToDelete) {
      if (device.weatherStation) {
        await prisma.weatherStation.delete({
          where: {
            id: device.weatherStation.id,
          },
        });
      }
    }

    // Delete the Devices with name "x"
    await prisma.device.deleteMany({
      where: {
        name: dev_name,
      },
    });
    
    return json(devicesToDelete.count)
  } catch (error) {
    console.error('Error deleting WeatherStations and Devices:', error);
  }  
  
}