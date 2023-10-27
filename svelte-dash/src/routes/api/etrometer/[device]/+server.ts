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
    where: where,
    orderBy: [{timestamp: 'asc'}],

    include: {
      etrometers: true,
    },
  });


  const transformedData = {};

  db_result.forEach(entry => {
    entry.etrometers.forEach(etrometer => {
      Object.keys(etrometer).forEach(key => {
        if (key !== "id" && key !== "timestamp" && key !== "name" && key !== "deviceId") {
          if (!transformedData[key]) {
            transformedData[key] = [];
          }
          transformedData[key].push({
            group: etrometer.name,
            date: new Date(Number(etrometer.timestamp)),
            value: etrometer[key]
          });
        }
      });
    });
  });

  return json(transformedData)
  //return json(db_result)
}