<script>
	import { Text } from '@threlte/extras'

	export let text = ''
	export let x = 0
	export let z = 0
	export let y = 0
	export let color = "#9a21bb"
	export let fontSize = 0.5
</script>

<Text
	{text}
	position.x={x}
	position.y={y}
	position.z={z}
	{color}
	{fontSize}
	rotation.x={-Math.PI / 2}
	rotation.z={Math.PI / 2 / 2}
	fillOpacity={1}
	anchorX="left"
/>
<!-- font={font} -->
