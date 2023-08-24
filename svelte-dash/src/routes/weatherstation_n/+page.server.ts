
import { base } from "$app/paths"
import type { PageServerLoad } from './$types';
//import { device_selected, } from '$lib/stores'
import { page } from '$app/stores';

import { get_wsv_range } from '$lib/prisma';

export const load: PageServerLoad = async ({ fetch, url, params}) => {
  
  const device_type = 'weatherstation_n'
  const response = await fetch(`${base}/api/devices/${device_type}`)
  const devices = await response.json();

  const range:BigInt[] = await get_wsv_range(url, params.device)  


  return {
    devices: devices.sort(),
    device_type: device_type,
    device_selected: devices.sort()[0],
    range: range // [Number(range[0]), Number(range[1])]
  }
}
