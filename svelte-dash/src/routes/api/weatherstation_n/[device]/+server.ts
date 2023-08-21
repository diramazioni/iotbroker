import { error, json } from "@sveltejs/kit";
import { prisma, get_wsv_range } from '$lib/prisma';


export async function GET({ url, params }) {

  const range:Date[] = get_wsv_range(url, params.device)

  //console.log(range[0])
  
  const db_result = await prisma.device.findMany({
    where: {
      name: { 'equals': params.device },
      weatherStation: {
        isNot: null,
      },
    },
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