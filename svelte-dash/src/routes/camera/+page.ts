
export const ssr = false;

export function load({ setHeaders }) {
	setHeaders({
		'Cache-Control': 'no-cache'
	});
}
