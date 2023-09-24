import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'
import { deviceKeys } from '$lib/constant'

import { jsonToCsv, filterDeviceKey, sliceCsv } from '$lib/shared'

export async function POST({ request, params, setHeaders }) {
	const { device_type, category_on } = await request.json()
	const device_key = deviceKeys[device_type]
	const keysToInclude = ['timestamp', ...category_on]
	const keysToExclude = ['id', 'deviceId']

	const db_result = await prisma.device.findMany({
		where: {
			name: { equals: params.device }
		},
		include: {
			weatherStation: true,
			etrometers: true,
			weatherStationVirtual: true
		}
	})
	if (db_result.length == 0) {
		console.log(`CSV POST No db data found  device_key ${device_key} device: ${params.device} ${keysToExclude} ${keysToInclude} category_on ${category_on}` )
		throw error(505, `CSV POST No db data found  device_key ${device_key} device: ${params.device} ${keysToExclude} ${keysToInclude} category_on ${category_on}` )
	}
	
	if (device_key == 'etrometers') {
		return new Response("etrometers csv export not supported")	
	}
	const filteredData = filterDeviceKey(db_result, device_key, keysToInclude, keysToExclude)
	if(filteredData[0]) {
		const csvContent = jsonToCsv(filteredData)
		setHeaders({
			//'Content-Type': 'text/csv'
			'Content-Type': 'text/plain'
		})
		return new Response(csvContent)	
	} else {
		console.log(`CSV POST No filtered data found  device_key ${device_key} device: ${params.device} ${keysToExclude} ${keysToInclude} category_on ${category_on}` )
		throw error(505, `CSV POST No filtered data found  device_key ${device_key} device: ${params.device} ${keysToExclude} ${keysToInclude} category_on ${category_on}` )
	}
}
