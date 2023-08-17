import { error, json } from "@sveltejs/kit";
import { prisma, get_wsv_range } from '$lib/prisma';


export async function GET({ url, params }) {

  const range:BigInt[] = get_wsv_range(url, params.device)
  const db_result = await prisma.device.findMany({
    where: {
      name: { 'equals': params.device },
      weatherStationVirtual: {
        isNot: null,
      },
      timestamp: {
        gte: range[0], // start
        lte: range[1]  // end
      }
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
      date: new Date(Number(timestamp)),
      value
    }));
  }).flat();

  return json(transformedData)
}