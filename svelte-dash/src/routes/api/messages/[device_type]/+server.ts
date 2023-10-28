import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'

export const prerender = false;

export async function GET({ request, params }) {
	const device_type = params.device_type
	const db_result = await prisma.messages.findMany({
		where: {
			device_type: { 
				'equals': device_type,
				mode: 'insensitive',
			},
		},
		orderBy:  { timestamp: 'asc' } 
	});
	const transformedData = db_result.map(entry => {
		const { timestamp, message } = entry;
		return message
	})
	return json(transformedData)

}
