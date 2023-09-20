<script>
	import { T } from '@threlte/core'
</script>

<T.Mesh receiveShadow position.y={-0.01} rotation.x={-90 * (Math.PI / 180)}>
	<T.CircleGeometry args={[30, 72]} />
	<T.MeshStandardMaterial />
</T.Mesh>
