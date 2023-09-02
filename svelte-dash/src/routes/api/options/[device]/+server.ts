import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';
import options from '$lib/options'


export async function GET({ url, params }) {

  const device_selected = params.device
  const firstRecord = await prisma.device.findFirst({
    where: {
      name: { 'equals': device_selected },
    },
    select: {timestamp: true, id:true },
    orderBy:  { timestamp: 'asc' } 
  });

  const lastRecord = await prisma.device.findFirst({
    where: {
      name: { 'equals': device_selected },
    },
    select: {timestamp: true, id:true },
    orderBy:  { timestamp: 'desc' } 
  });
  let extOptions = { 
    ...options,  
    title: device_selected,
    zoomBar: {
      top : {
        enabled : true,
        initialZoomDomain: [firstRecord?.timestamp, lastRecord?.timestamp],
      }
    }
  }
  
  return json(extOptions)
}