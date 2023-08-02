
import { prisma }  from '$lib/prisma';
import type { PageServerLoad } from './$types';

// export const load = (async () => {

//   // where: { published: true },
//   // include: { author: true },

// const response = await prisma.device.findMany()

// return { obj: response };

// }) satisfies PageServerLoad;

export const load: PageServerLoad = async () => {
  const response = await prisma.device.findMany()
  console.log(response)
	return {
		devices: response
	}
}