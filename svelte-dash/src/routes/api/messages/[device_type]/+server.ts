// https://greenlab.unibo.it/iot/api/messages/WeatherStation_n?start=2023-10-14T17:55:30.000Z&end=2023-10-30T18:55:30.000Z
import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'

export const prerender = false;

export async function GET({ url, params }) {
	const startParam = url.searchParams.get('start');
	const endParam = url.searchParams.get('end');
	const where = {
		device_type: { 
			'equals': device_type,
			mode: 'insensitive',
		},
	}
	if (startParam && endParam) {
		where['timestamp'] = {
			gte: startParam, // start
			lte: endParam  // end
		}
	}	
	const device_type = params.device_type
	const db_result = await prisma.messages.findMany({
		where:  where,
		orderBy:  { timestamp: 'asc' } 
	});
	const transformedData = db_result.map(entry => {
		const { timestamp, message } = entry;
		return message
	})
	return json(transformedData)

}
