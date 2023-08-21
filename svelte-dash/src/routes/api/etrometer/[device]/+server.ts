import { error, json } from "@sveltejs/kit";
import { prisma, get_wsv_range } from '$lib/prisma';


export async function GET({ url, params }) {

  //const range:BigInt[] = get_wsv_range(url, params.device)

  //console.log(range[0])
  
  const db_result = await prisma.device.findMany({
    where: {
      name: { 'equals': params.device },
      etrometers: {
        some: {} // This condition ensures at least one ETRometer is associated
      },

    },
    include: {
      etrometers: true
    }
  });

  // timestamp: {
  //   gte: range[0], // start
  //   lte: range[1]  // end
  // }

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