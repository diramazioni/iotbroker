
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
  let response = await fetch('/api/weatherstation_n')
  const weatherstation_n = await response.json();
  response = await fetch('/api/weatherstation_v')
  const weatherstation_v = await response.json();
  response = await fetch('/api/etrometer')
  const etrometer = await response.json();  
  //return { weatherstation };

	return {
		weatherstation_n: weatherstation_n,
    weatherstation_v: weatherstation_v,
    etrometer: etrometer
	}
}
