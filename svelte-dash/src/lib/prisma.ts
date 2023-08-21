import { PrismaClient } from "@prisma/client"
import { env } from "$env/dynamic/private"
import { error, json } from "@sveltejs/kit"

const prisma = global.__prisma || new PrismaClient()

if (env.NODE_ENV === "development") {
	global.__prisma = prisma
}

export { prisma }

export async function get_wsv_range(url: URL, device:string ) {

  const startParam = url.searchParams.get('start');
  const endParam = url.searchParams.get('end');

  // Convert start and end to BigInt, or provide defaults based on the first and last records
  const firstRecord = await prisma.device.findFirst({
    where: {
      name: { 'equals': device },
      //weatherStationVirtual: { 'isNot': null }
    },
    select: {timestamp: true,  },
    orderBy:  { timestamp: 'asc' } 
  });

  const lastRecord = await prisma.device.findFirst({
    where: {
      name: { 'equals': device },
      //weatherStationVirtual: { 'isNot': null }
    },
    select: {timestamp: true, },
    orderBy:  { timestamp: 'desc' } 
  });

  const defaultStart = Date(firstRecord.timestamp) //?? 0n;
  const defaultEnd = Date(lastRecord?.timestamp) //?? 1n;

  const start = startParam ? Date(startParam) : defaultStart;
  const end = endParam ? Date(endParam) : defaultEnd;

  if (start > end) {
    throw error(400, 'Invalid start/end parameters.');
  }

  const range = [start,end]
  return range
}