import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';


export async function GET({ url, params }) {

  //console.log(range[0])
  
  const db_result = await prisma.device.findMany({
    where: {
      name: { 'equals': params.device },
      weatherStationVirtual: {
        isNot: null,
      },
      // timestamp: {
      //   gte: range[0], // start
      //   lte: range[1]  // end
      // }
    },
    include: {
      weatherStationVirtual: true
    }
  });


  const transformedData = db_result.map(entry => {
    const { timestamp, weatherStationVirtual } = entry;
    
    return Object.entries(weatherStationVirtual)
    .filter(([key]) => key !== "id" && key !== "timestamp" && key !== "deviceId")
    .map(([group, value]) => ({
      group,
      date: new Date(timestamp),
      value
    }));
  }).flat();

  return json(transformedData)
}