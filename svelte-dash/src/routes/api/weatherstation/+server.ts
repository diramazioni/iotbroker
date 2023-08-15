import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url }) {
  /*   
  const start = Number(url.searchParams.get('start') ?? '0');
  const end = Number(url.searchParams.get('end') ?? '1');
  const d = end - start;
  if (isNaN(d) || d < 0) {
    throw error(400, 'start and end must be numbers, and start must be less than end');
  }
   */
  const db_result = await prisma.device.findMany({
    where: { weatherStation: { 'isNot': null } },
    include: {
      weatherStation: true
    }
  })

  const transformedData = db_result.map(entry => {
    const { timestamp, weatherStation } = entry;
    
    return Object.entries(weatherStation)
    .filter(([key]) => key !== "id" && key !== "timestamp" && key !== "deviceId")
    .map(([group, value]) => ({
      group,
      date: new Date(Number(timestamp)),
      value
    }));
  }).flat();

  return json(transformedData)
}