<script>
	import { T } from '@threlte/core'
	import { OrbitControls } from '@threlte/extras'
	import { OrthographicCamera } from 'three'

	let SCREEN_WIDTH = window.innerWidth;
	let SCREEN_HEIGHT = window.innerHeight;
	let aspect = SCREEN_WIDTH / SCREEN_HEIGHT;
	const frustumSize = 600;

	let left = SCREEN_WIDTH / -2 // 0.5 * frustumSize * aspect / - 2
	let right = SCREEN_WIDTH / 2
	const top = SCREEN_HEIGHT / 2 // frustumSize / 2
	const bottom = SCREEN_HEIGHT / - 2 // frustumSize / - 2
	const near = 0.1
	const far = 1000

</script>
<!-- 
left={-1}
right={1}
top={1}
bottom={-1}
near={near}
far={far} -->
<T.OrthographicCamera 
	makeDefault
	position={[0, 0, 20]}
	zoom={50}
	>

	<!-- args={ [left, right, top, bottom, near, far]} -->
	<OrbitControls enableDamping  target={[0, 0, 0]}/> 
</T.OrthographicCamera>

