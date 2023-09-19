// place files you want to import through the `$lib` alias in this folder.
import { base } from '$app/paths'
// export function propertyFromArray<T>(dataArray: T[], property: keyof T): Array<T[keyof T]> {
//   return dataArray.map(item => item[property]);
// }

// export function propertyFromWeatherData(dataArray: Device[], property: keyof WeatherStation): Array<any> {
//   return dataArray.map(item => item.weatherStation[property]);
// }

type Fetch = (input: RequestInfo | URL, init?: RequestInit | undefined) => Promise<Response>

export async function fetch_data(fetch: Fetch, device_type: string, device_selected: string) {
	const url = `${base}/api/${device_type}/${device_selected}`
	console.log(`fetch_data ${url}`)
	const response = await fetch(url)
	const json = await response.json()
	//console.log(JSON.stringify(json))
	return json
}

export async function fetch_opt(fetch: Fetch, device_type: string, device_selected: string) {
	const url = `${base}/api/options/${device_type}/${device_selected}`
	console.log(`fetch_opt ${url}`)
	const response = await fetch(url)
	const json = await response.json()
	return json
}

export async function fetch_dev(fetch: Fetch, device_type: string) {
	const url = `${base}/api/devices/${device_type}`
	console.log(`fetch_dev ${url}`)
	const response = await fetch(url)
	const json = await response.json()
	return json
}

export async function fetch_CSV(fetch: Fetch, device_key: string, device_selected: string, category_on:string[]) {
	const url = `${base}/api/csv/${device_selected}`
	console.log(`fetch_CSV ${url} ${device_key} ${category_on}`)
	const response = await fetch(url, {
		method: 'POST',
		body: JSON.stringify({ device_key, category_on }),
		headers: {
			'Content-Type': 'application/json'
		}
	})
	const text = await response.text()
	if (response.ok) {
		return text
	} else {
		throw new Error(text)
	}
}

export function sliceCsv (csvData:string, maxData:number) {
	const lines = csvData.split('\n')
	const back = maxData < lines.length ? lines.length - maxData : 1
	const header = lines[0]
	const last_lines = lines.slice(back, lines.length)
	// console.log([back, lines.length])
	// console.log(last_lines.length)
	return [header, ...last_lines].join('\n')
}


export function jsonToCsv(jsonData) {
	const csvHeader = Object.keys(jsonData[0]).join(',')
	const csvData = jsonData.map((obj) => Object.values(obj).join(',')).join('\n')
	return `${csvHeader}\n${csvData}`
}

export function filterDeviceKey(
	array: [],
	deviceKey: string,
	keysToInclude: string[],
	keysToExclude: string[]
) {
	return array.map((dataObj) => {
		//console.log("dk  "+ deviceKey)
		const extractedObject = dataObj[deviceKey]
		if (extractedObject) {
			const filteredData = Object.fromEntries(
				Object.entries(extractedObject).filter(([key]) => {
					if (keysToInclude.length === 1 && keysToInclude[0] === 'timestamp') {
						// If keysToInclude contains only 'timestamp', include all keys except the excluded ones
						return !keysToExclude.includes(key);
					} else {
						// Always include 'timestamp' and other keys specified in keysToInclude
						return key === 'timestamp' || keysToInclude.includes(key);
					}
				})
			)
			return filteredData
		}
	})
}

export function filterObjectKey(
	objectToFilter: {},
	keysToInclude: string[]=[],
	keysToExclude: string[]=[]
) {
	const filteredData = Object.fromEntries(
		Object.entries(objectToFilter).filter(([key]) => {
			if (keysToInclude.length === 0 ) {
				return !keysToExclude.includes(key);
			} else {
				return keysToInclude.includes(key);
			}
		})
	)
	return filteredData
}