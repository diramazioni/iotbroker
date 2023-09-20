import { base } from '$app/paths'
import type { PageServerLoad } from './$types'
import { fetch_dev, fetch_CSV, sliceCsv } from '$lib/shared'
import { deviceKeys } from '$lib/constant'

export const load: PageServerLoad = async ({ fetch, url, params }) => {
	const device_type = params.device_type
	const device_key = deviceKeys[device_type]
	const devices = await fetch_dev(fetch, device_type)
	const device_selected = devices.sort()[0]
	let device_csv = await fetch_CSV(fetch, device_type, device_selected, [])
	const lines = device_csv.split('\n')
	const categories = lines[0].split(',')
	const max_lines = lines.length - 1
	device_csv = sliceCsv(device_csv, 30)


	return {
		devices: devices.sort(),
		device_type: device_type,
		device_selected: device_selected,
		device_csv: device_csv,
		categories:categories.slice(1,categories.length),
		max_lines: max_lines,
	}
}
