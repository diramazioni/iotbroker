
import { prisma }  from '$lib/prisma';
import type { PageServerLoad } from './$types';
import {propertyFromArray, propertyFromWeatherData} from '$lib/index';

export const load: PageServerLoad = async () => {
  const response = await prisma.device.findMany({
    where: { weatherStation: {'isNot': null } },
    include: {
      weatherStation: true
    }
  })
  console.log(response)
  //const temperatures: number[] = propertyFromArray(response, 'Temperature');
  const temperatures: number[] = propertyFromWeatherData(response, 'Temperature');

  console.log(temperatures)
	return {
		device: response,
    temperatures: temperatures
	}
}