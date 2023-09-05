// place files you want to import through the `$lib` alias in this folder.
import { base } from "$app/paths";
// export function propertyFromArray<T>(dataArray: T[], property: keyof T): Array<T[keyof T]> {
//   return dataArray.map(item => item[property]);
// }

// export function propertyFromWeatherData(dataArray: Device[], property: keyof WeatherStation): Array<any> {
//   return dataArray.map(item => item.weatherStation[property]);
// }


export async function fetch_data(fetch, device_type:string , device_selected:string) {
    const url = `${base}/api/${device_type}/${device_selected}`;
    console.log(`fetch_data ${url}`)
    const response = await fetch(url)
    let json = await response.json()
    //console.log(JSON.stringify(json))
    return json
}

export async function fetch_opt(fetch, device_type:string, device_selected:string) {
    const url = `${base}/api/options/${device_type}/${device_selected}`;
    console.log(`fetch_opt ${url}`)
    const response = await fetch(url)
    let json = await response.json()
    return json
} 

export async function fetch_dev(fetch, device_type:string) {
  let url = `${base}/api/devices/${device_type}`;
  console.log(`fetch_dev ${url}`)
  const response = await fetch(url)
  let json = await response.json()
  return json
}