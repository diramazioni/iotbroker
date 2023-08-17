import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

/*
const uniqueDeviceNames = await prisma.device.groupBy({
  by: ['name'],
  _count: {
    name: true
  }
});
*/

export async function GET({ url, params }) {
  const db_result = await prisma.device.findMany({
    where: {
      name: { 'contains': params.devicetype},
    },
  });
  const deviceNamesSet = new Set();
  db_result.forEach(device => deviceNamesSet.add(device.name));
  const deviceNamesArray = Array.from(deviceNamesSet);

  return json(deviceNamesArray)
}