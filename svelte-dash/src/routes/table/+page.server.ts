
import { prisma }  from '$lib/prisma';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
  const response = await prisma.device.findMany({
    where: { weatherStation: {'isNot': null } },
    include: {
      weatherStation: true
    }
  })
  console.log(response)
	return {
		devices: response
	}
}