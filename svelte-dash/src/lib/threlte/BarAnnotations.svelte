<script>
	import { Text } from '@threlte/extras'

	export let d = ""
	export let x = 0
	export let y = 0
	export let z = 0

</script>

<Text
	text={d}
	position.x={x - 0.3}
	position.y={y + 0.01}
	position.z={z}
	color="#230612"
	fontSize={0.4}
	rotation.x={-Math.PI / 2}
	rotation.z={Math.PI / 2}
	fillOpacity={1}
	anchorX="center"
/>
