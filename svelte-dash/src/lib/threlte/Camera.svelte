<script>
	import { T } from '@threlte/core'
	import { OrbitControls } from '@threlte/extras'
</script>

<T.PerspectiveCamera
	makeDefault
	position={[22, 8, 15]}
	on:create={({ ref }) => {
		ref.lookAt(20, 0, 0)
	}}
>
	<OrbitControls enableDamping target={[0, -5, 0]} />
</T.PerspectiveCamera>

