export const deviceKeys = {
    weatherstation_n: 'weatherStation',
    weatherstation_v: 'weatherStationVirtual',
    etrometer: 'etrometers'
}

import { base } from '$app/paths'
export 	const menu = [
    {
        name: 'Home',
        href: `${base}/`,
    },{
        name: 'Weather Stations',
        href: `${base}/d/weatherstation_n`,
    },
    // {
    //     name: 'Virtual Weather Stations',
    //     href: `${base}/d/weatherstation_v`,
    // },
    {
        name: 'Etrometers',
        href: `${base}/d/etrometer`,
    },{
        name: 'Cameras',
        href: `${base}/camera`,
    }
]