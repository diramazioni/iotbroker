import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';


export async function GET({ url, params }) {
  const device_selected = params.device
  const startParam = url.searchParams.get('start');
  const endParam = url.searchParams.get('end');
	const where = {
    device: {
      name: { equals: device_selected },
    },
  }

	if (startParam && endParam) {
		where['timestamp'] = {
			gte: startParam, // start
			lte: endParam  // end
		}
	}
  const query = {
    where:  where,
    orderBy: [{timestamp: 'asc'}],
    include: {
      device: true,
    }
  }
  const db_result = await prisma.weatherStationVirtual.findMany(query);
  // console.log(query)

  const transformedData = db_result.map(entry => {
    const { id, timestamp, device, deviceId, ...rest } = entry;
    // console.log(rest)
    return Object.entries(rest)
    .map(([group, value]) => ({
      group,
      date: new Date(timestamp),
      value
    }));
  }).flat();

  return json(transformedData)
}