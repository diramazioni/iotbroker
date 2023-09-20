<script>
	import { Text } from '@threlte/extras'

	export let text = ''
	export let x = 0
	export let z = 0
	export let y = 0
	export let color = "#3c21bb"
	export let fontSize = 0.5
</script>

<Text
	{text}
	position.x={x - 0.03}
	position.y={y + 0.01}
	position.z={z - 0.55}
	{color}
	{fontSize}
	rotation.x={-Math.PI / 2}
	rotation.z={Math.PI / 2}
	fillOpacity={1}
	anchorX="right"
/>
