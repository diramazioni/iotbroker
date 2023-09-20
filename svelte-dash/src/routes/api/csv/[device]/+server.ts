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
		console.log("No data found for device " + params.device)
		console.log(device_key )
		throw error(505, `No data found for device ${params.device}`)
	}
}