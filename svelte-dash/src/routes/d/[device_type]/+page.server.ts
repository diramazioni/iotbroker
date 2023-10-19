
import { base } from "$app/paths"
import type { PageServerLoad } from './$types';
//import { device_selected, } from '$lib/stores'
import { page } from '$app/stores';
import { fetch_data, fetch_opt, fetch_dev, fetch_range} from '$lib/shared';

export const load: PageServerLoad = async ({ fetch, url, params}) => {
  
  const device_type = params.device_type
  //const response = await fetch(`${base}/api/devices/${device_type}`)
  const devices = await fetch_dev(fetch, device_type);
  const device_selected = devices.sort()[0]
  let ranges =  await fetch_range(fetch, device_selected);
  ranges = ranges.slice(1)
  const range = [new Date(ranges[0]), new Date(ranges[1])]
  const device_data = await fetch_data(fetch, device_type, device_selected, range);
  const device_opt = await fetch_opt(fetch, device_type, device_selected, range);

  return {
    devices: devices.sort(),
    device_type: device_type,
    device_selected: device_selected,
    device_data: device_data,
    device_opt: device_opt,
  }
}
