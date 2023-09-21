<script>
	import { T } from '@threlte/core'
	import { interactivity, Text } from '@threlte/extras'
	import { onMount } from 'svelte'
	import { spring } from 'svelte/motion'

	interactivity()
	// export let selectedYear;
	// export let year;
	export let i = 0
	export let x = 0
	export let y = 0
	export let z = 0
	export let color = "#ffffff"
	export let value = 0
	export let castShadow = false
	export let receiveShadow = false

	//z = z ? z : i
	const text = Number(value.toFixed(1)); 
	const height = spring(0.1)
	const hover = spring(0)

	onMount(() => {
		height.set(y)
	})
</script>

<!-- {console.log(z)} -->

<T.Mesh
	position.x={x}
	position.y={$height / 2 + $hover + 0.01}
	position.z={z}
	scale.y={$height}
	on:pointerenter={() => hover.set(1)}
	on:pointerleave={() => hover.set(0)} 

>
	<!-- 
		{castShadow}
		{receiveShadow}
	-->

	<T.BoxGeometry args={[0.1, 1, 0.5]} />
	<T.MeshLambertMaterial {color} />
	<!-- 
	<T.MeshStandardMaterial {color} />
	<T.MeshLambertMaterial {color} />
	<T.MeshMatcapMaterial {color} /> -->
</T.Mesh>

<Text
	text={text}
	position.x={x}
	position.y={($height + $hover ) +0.8}
	position.z={z}
	{color}
	fontSize={0.8}
	fillOpacity={$hover}
	anchorX="center"
/>
