import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ setHeaders}) => {
	setHeaders({
		'Cache-Control': 'no-cache'
	});
}
