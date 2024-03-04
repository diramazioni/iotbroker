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
  const db_result = await prisma.eTRometer.findMany(query);
// console.log(query)

  const transformedData = {};
  db_result.forEach(entry => {
    const { id, timestamp, device, deviceId, ...rest } = entry;
    // console.log(rest)

      Object.keys(rest).forEach(key => {
        if (!transformedData[key]) {
          transformedData[key] = [];
        }
        transformedData[key].push({
          group: rest.name,
          date: new Date(Number(timestamp)),
          value: rest[key]
        });
      });
  });

  // db_result.forEach(entry => {
  //   entry.etrometers.forEach(etrometer => {
  //     Object.keys(etrometer).forEach(key => {
  //       if (key !== "id" && key !== "timestamp" && key !== "name" && key !== "deviceId") {
  //         if (!transformedData[key]) {
  //           transformedData[key] = [];
  //         }
  //         transformedData[key].push({
  //           group: etrometer.name,
  //           date: new Date(Number(etrometer.timestamp)),
  //           value: etrometer[key]
  //         });
  //       }
  //     });
  //   });

  return json(transformedData)
  //return json(db_result)
}