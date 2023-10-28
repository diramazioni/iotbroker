import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const dev_name = params.device
  try {
    // Find all Devices with name "x"
    const devicesToDelete = await prisma.device.findMany({
      where: {
        name: dev_name,
      },
      include: {
        weatherStation: true, // Include the associated WeatherStation
        weatherStationStd: true,
        weatherStationVirtual: true
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

    // Delete the Devices with name "x"
    await prisma.device.deleteMany({
      where: {
        name: dev_name,
      },
    });
    
    return json(devicesToDelete.length)
  } catch (error) {
    console.error('Error deleting WeatherStations and Devices:', error);
  }  
  
}