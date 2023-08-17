import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  /*   
  const start = Number(url.searchParams.get('start') ?? '0');
  const end = Number(url.searchParams.get('end') ?? '1');
  const d = end - start;
  if (isNaN(d) || d < 0) {
    throw error(400, 'start and end must be numbers, and start must be less than end');
  }
   */
  const db_result = await prisma.device.findMany({
    where: {
      etrometers: {
        some: {} // This condition ensures at least one ETRometer is associated
      }
    },
    include: {
      etrometers: true
    }
  })


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
}