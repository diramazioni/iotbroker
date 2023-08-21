
import type { PageLoad } from './$types';
//import { device_selected, } from '$lib/stores'

export const load: PageLoad = async ({ fetch, data,}) => {
  
  const ds = (data.device_selected.length === 0 ) ? data.devices.sort()[0] : data.device_selected
  return {
    ...data,
    // device_selected: ds, 
  }
}
