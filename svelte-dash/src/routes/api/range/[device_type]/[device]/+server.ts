import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'

export const prerender = false;

export async function GET({ request, params }) {
	const device_selected = params.device
	const device_type = params.device_type
	// const firstRecord = await prisma.device.findFirst({
	// 	where: {
	// 		name: { 'equals': device_selected },
	// 	},
	// 	select: {timestamp: true, id:true },
	// 	orderBy:  { timestamp: 'asc' } 
	// });
	// const lastRecord = await prisma.device.findFirst({
	// 	where: {
	// 		name: { 'equals': device_selected },
	// 	},
	// 	select: {timestamp: true, id:true },
	// 	orderBy:  { timestamp: 'desc' } 
	// });
	const firstRecordQ = {
		where: {
			device: {
				name: { equals: device_selected },
			},
		},
		include: {
			device: true,
		},
		orderBy:  { timestamp: 'asc' } 
	};
	const lastRecordQ = {
		where: {
			device: {
				name: { equals: device_selected },
			},
		},
		include: {
			device: true,
		},
		orderBy:  { timestamp: 'desc' } 
	};

	let firstRecord, lastRecord;
	if (device_type === 'weatherstation_n') {
		firstRecord = await prisma.weatherStation.findFirst(firstRecordQ);
		lastRecord = await prisma.weatherStation.findFirst(lastRecordQ);
	} else if (device_type === 'weatherstation_s') {
		firstRecord = await prisma.weatherStationStd.findFirst(firstRecordQ);
		lastRecord = await prisma.weatherStationStd.findFirst(lastRecordQ);
	} else if (device_type === 'weatherstation_v') {
		firstRecord = await prisma.weatherStationVirtual.findFirst(firstRecordQ);
		lastRecord = await prisma.weatherStationVirtual.findFirst(lastRecordQ);
	} else if (device_type === 'etrometer') {
		console.log("etrometer")
		firstRecord = await prisma.eTRometer.findFirst(firstRecordQ);
		lastRecord = await prisma.eTRometer.findFirst(lastRecordQ);
	} else {
		throw Error("Invalid device type")
	}

	const firstDate = new Date(firstRecord?.timestamp)
	const lastDate = new Date(lastRecord?.timestamp)
	let viewDate = new Date(lastDate);
	viewDate.setDate(lastDate.getDate() - 15); // take the last 15 days
	if (viewDate.getTime() < firstDate.getTime()) {  // use first record if there is no data 15days before
		viewDate = firstDate;
	}	
	return json([firstDate, viewDate, lastDate])
}
