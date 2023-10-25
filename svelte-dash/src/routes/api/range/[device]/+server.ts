import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'

export const prerender = false;

export async function GET({ request, params }) {
	const device_selected = params.device
	const firstRecord = await prisma.device.findFirst({
		where: {
			name: { 'equals': device_selected },
		},
		select: {timestamp: true, id:true },
		orderBy:  { timestamp: 'asc' } 
	});
	const lastRecord = await prisma.device.findFirst({
		where: {
			name: { 'equals': device_selected },
		},
		select: {timestamp: true, id:true },
		orderBy:  { timestamp: 'desc' } 
	});
	const firstDate = new Date(firstRecord?.timestamp)
	const lastDate = new Date(lastRecord?.timestamp)
	let viewDate = new Date(lastDate);
	viewDate.setDate(lastDate.getDate() - 15); // take the last 15 days
	if (viewDate.getTime() < firstDate.getTime()) {  // use first record if there is no data 15days before
		viewDate = firstDate;
	}	
	return json([firstDate, viewDate, lastDate])
}
