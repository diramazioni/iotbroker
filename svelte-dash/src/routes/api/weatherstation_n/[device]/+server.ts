import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';


export async function GET({ url, params }) {
  const startParam = url.searchParams.get('start');
  const endParam = url.searchParams.get('end');
	const where = {	name: { equals: params.device } }
	if (startParam && endParam) {
		where['timestamp'] = {
			gte: startParam, // start
			lte: endParam  // end
		}
	}
  const db_result = await prisma.device.findMany({
    where:  where,
    orderBy: [{timestamp: 'asc'}],
    include: {
      weatherStation: true
    }
  });


  const transformedData = db_result.map(entry => {
    const { timestamp, weatherStation } = entry;
    
    return Object.entries(weatherStation)
    .filter(([key]) => key !== "id" && key !== "timestamp" && key !== "deviceId")
    .map(([group, value]) => ({
      group,
      date: new Date(timestamp),
      value
    }));
  }).flat();

  return json(transformedData)
}