<script>
	import { T } from '@threlte/core'
	import { BufferGeometry, Float32BufferAttribute } from 'three'

	export let vertices 
	export let colors


	let buff
	$: buff?.setAttribute('position', new Float32BufferAttribute(vertices, 3))
	$: buff?.setAttribute('color', new Float32BufferAttribute(colors, 3))


</script>

<T.Points>
	<T.BufferGeometry bind:ref={buff} />
	<T.PointsMaterial size=0.1 vertexColors=true/>
</T.Points>
