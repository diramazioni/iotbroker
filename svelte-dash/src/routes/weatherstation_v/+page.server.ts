
import type { PageServerLoad } from './$types';
//import { device_selected, } from '$lib/stores'
import { page } from '$app/stores';


export const load: PageServerLoad = async ({ fetch, params}) => {
  
  const device_type = 'weatherstation_v'
  const response = await fetch('/api/devices/WeatherStation_v')
  const devices = await response.json();



  return {
    devices: devices.sort(),
    device_type: device_type,
    device_selected: devices.sort()[0] , 
  }
}
