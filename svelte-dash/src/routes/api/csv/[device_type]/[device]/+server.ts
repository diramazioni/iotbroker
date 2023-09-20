import { error, json } from '@sveltejs/kit'
import { prisma } from '$lib/prisma'
import { deviceKeys } from '$lib/constant'
import { jsonToCsv, filterDeviceKey, sliceCsv } from '$lib/shared'

export const prerender = false;

export async function GET({ request, params, setHeaders }) {
	const db_result = await prisma.device.findMany({
		where: {
			name: { equals: params.device },
		},
		include: {
			weatherStation: true,
			etrometers: true,
			weatherStationVirtual: true,
		}
	})
	const category_on = []
	const keysToInclude = ['timestamp', ...category_on]
	const keysToExclude = ['id', 'deviceId']
	const device_key = deviceKeys[params.device_type]
	const filteredData = filterDeviceKey(db_result, device_key, keysToInclude, keysToExclude)
	if(filteredData[0]) {
		const csvContent = jsonToCsv(filteredData)
		setHeaders({
			//'Content-Type': 'text/csv'
			'Content-Type': 'text/plain'
		})
		return new Response(csvContent)	
	} else {
		return new Response(`No data found for device ${params.device_type}`)	
	}
}
