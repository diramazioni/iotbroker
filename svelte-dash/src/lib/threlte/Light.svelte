<script>
	import { T } from '@threlte/core'
	export let col1 = "#ffffff"
	export let col2 = "#000000"
</script>
<!-- 
<T.DirectionalLight castShadow position={[10, 20, 5]}>
	<T.PerspectiveCamera
		attach="shadow.camera"
		left={-100}
		right={100}
		top={100}
		bottom={-100}
		near={1}
		far={10000}
	/>
	<T.Vector2 attach="shadow.mapSize" args={[4196, 4196]} />
</T.DirectionalLight> -->

<T.HemisphereLight args={[col1, col2, 0.5]} />
<T.DirectionalLight position={[10, 20, 5]}>
</T.DirectionalLight>