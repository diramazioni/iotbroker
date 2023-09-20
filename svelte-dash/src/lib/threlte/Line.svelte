<script>
	import { T } from '@threlte/core'
	import { SplineCurve, LineCurve3 } from 'three'

	export let points3d 
	export let color
	/*
	const curve = new LineCurve3(points);
	const point_curve = curve.getPoints( 50 );
	*/
</script>

<T.Line>
	<T.BufferGeometry on:create={({ ref }) => {
		ref.setFromPoints(points3d)
	  }} />
	<T.LineBasicMaterial {color}/>
</T.Line>
