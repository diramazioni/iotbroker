
import { prisma }  from '$lib/prisma';
import type { PageServerLoad } from './$types';
import {propertyFromArray, propertyFromWeatherData} from '$lib/index';

export const load: PageServerLoad = async ({ fetch, params }) => {
  let response = await fetch('/api/weatherstation')
  const weatherstation = await response.json();
  response = await fetch('/api/weatherstation_virt')
  const weatherstation_virt = await response.json();
  response = await fetch('/api/etrometer')
  const etrometer = await response.json();  
  //return { weatherstation };

	return {
		weatherstation: weatherstation,
    weatherstation_virt: weatherstation_virt,
    etrometer: etrometer
	}
}