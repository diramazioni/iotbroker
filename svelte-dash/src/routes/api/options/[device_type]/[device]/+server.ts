import { error, json } from "@sveltejs/kit";
import { prisma } from '$lib/prisma';
import options from '$lib/options'


export async function GET({ url, params }) {

  const device_type = params.device_type
  const device_selected = params.device
  const startParam = url.searchParams.get('start');
  const endParam = url.searchParams.get('end');
  let extOptions = { 
    ...options,  
    title: device_selected,
    zoomBar: {
      top : {
        enabled : true,
        initialZoomDomain: [startParam, endParam],
      }
    }
  }
  if (device_type === 'etrometer') {

    const etr = {
      CO2: { ...extOptions,  title: `${device_selected} CO2` },
      TC: { ...extOptions,  title: `${device_selected} TC` },
      RH: { ...extOptions,  title: `${device_selected} RH` },
    }
    return json(etr)
  } else {
    return json(extOptions)
  }
}