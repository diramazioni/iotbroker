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
    },
    {
        name: 'WS New',
        href: `${base}/d/weatherstation_n`,
    },
    {
        name: 'WS Standard',
        href: `${base}/d/weatherstation_s`,
    },
    {
        name: 'Virtual WS',
        href: `${base}/d/weatherstation_v`,
    },
    {
        name: 'Etrometers',
        href: `${base}/d/etrometer`,
    },{
        name: 'Cameras',
        href: `${base}/camera`,
    }
]