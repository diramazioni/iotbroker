
import type { LayoutServerLoad } from './$types';
//import {device_selected} from '$lib/stores'

export const load: LayoutServerLoad = async ({ fetch, params }) => {
  //console.log("")
	// let response = await fetch('/api/devices/WeatherStation_n')
  // const devices_WeatherStation_n = await response.json();
  // return {
	// 	devices: devices_WeatherStation_n,
	// }
  return {
    incoming: []
  }
}
