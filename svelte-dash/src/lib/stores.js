import { readable, writable, derived } from 'svelte/store'

// export const device_selected = writable('');
// export const device_type = writable('');

export const PAR = writable({})

export const socketStore = writable(null)

export const breakpoints = {
    'sm': '(min-width: 640px)',
    'md': '(min-width: 768px)',
    'lg': '(min-width: 1024px)',
    'xl': '(min-width: 1280px)',
    '2xl': '(min-width: 1536px)'
};

/**
 * Stores the current window size
 * @param {string} query
 */
export function mediaQueryStore(query) {
	if (typeof window === 'undefined') {
		// check if it's rendered in the dom so window is not undefined
		return readable('');
	}
	const mediaQueryList = window.matchMedia(query);

	const mediaStore = readable(mediaQueryList.matches, (set) => {
		const handleChange = () => set(mediaQueryList.matches);

		try {
			mediaQueryList.addEventListener('change', handleChange);
		} catch (_) {
			mediaQueryList.addListener(handleChange);
		}

		return () => {
			try {
				mediaQueryList.removeEventListener('change', handleChange);
			} catch (_) {
				mediaQueryList.removeListener(handleChange);
			}
		};
	});

	return mediaStore;
}
