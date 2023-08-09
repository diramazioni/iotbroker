// place files you want to import through the `$lib` alias in this folder.

export function propertyFromArray<T>(dataArray: T[], property: keyof T): Array<T[keyof T]> {
  return dataArray.map(item => item[property]);
}

export function propertyFromWeatherData(dataArray: Device[], property: keyof WeatherStation): Array<any> {
  return dataArray.map(item => item.weatherStation[property]);
}
