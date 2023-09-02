
import { base } from "$app/paths"
import type { PageServerLoad } from './$types';
//import { device_selected, } from '$lib/stores'
import { page } from '$app/stores';


export const load: PageServerLoad = async ({ fetch, url, params}) => {
  
  const device_type = 'etrometer'
  const response = await fetch(`${base}/api/devices/${device_type}`)
  const devices = await response.json();

  return {
    devices: devices.sort(),
    device_type: device_type,
    device_selected: devices.sort()[0],
  }
}
