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
	export let color = "#230612"
	export let value = ""
	export let castShadow = false
	export let receiveShadow = false

	//z = z ? z : i

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
	{castShadow}
	{receiveShadow}

>
	<!-- 
		on:pointerenter={() => hover.set(1)}
		on:pointerleave={() => hover.set(0)} 
	-->

	<T.ConeGeometry args={[0.3, 1, 4]} />
	<T.MeshStandardMaterial {color} transparent={true} opacity={0.4} />
</T.Mesh>
<!-- 
<Text
	text={value}
	position.x={x}
	position.y={($height + $hover ) +0.8}
	position.z={z}
	color="#230612"
	fontSize={0.8}
	fillOpacity={$hover}
	anchorX="center"
/> -->
