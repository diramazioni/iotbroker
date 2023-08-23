import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';

export async function GET({ url, params }) {
  const deletedDevices = await prisma.device.deleteMany({
    where: {
      name: 'WeatherStation_n_test'
    }
  });
  
  console.log(`Deleted ${deletedDevices.count} devices`); 
  return json(deletedDevices.count)
}