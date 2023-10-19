<!-- https://www.datavizcubed.com -->
<script lang='ts'>
	import { onMount } from 'svelte'
	import { browser } from '$app/environment'

	import { T } from '@threlte/core'
	import * as d3 from 'd3'
	import { Pane } from 'tweakpane'
	import { Float32BufferAttribute, PlaneGeometry, Vector2, Vector3 } from 'three'
	import { DEG2RAD } from 'three/src/math/MathUtils'

	import { IBM_palette_light, IBM_palette_dark, hsv2rgb } from '$lib/colors'
	import { PAR } from '$lib/stores'

	import Bar from './Bar.svelte'
	import Cone from './Cone.svelte'
	import Point from './Point.svelte'
	import Line from './Line.svelte'
	import Area from './Area.svelte'
	import Floor from './Floor.svelte'
	import CameraPerpective from './CameraPerpective.svelte'
	import CameraOrto from './CameraOrto.svelte'
	import Light from './Light.svelte'
	import XLabels from './XLabels.svelte'
	import CatLabels from './CatLabels.svelte'
	import Title from './Title.svelte'
	import Grid from './Grid.svelte'

	export let csv_data = ""
	
	//export let categories = []
	export let range_x = [-10, 10]
	export let range_y = [0, 5]
	export let range_z = [0, 10]
	export let max_data = 100


	const csv = d3.csvParse(csv_data, d3.autoType) 
	//$: console.log(csv)
	const total = csv.length
	const categories = csv.columns.filter((item) => item !== 'timestamp')
	const timestamps_ = [...new Set(csv.map((d) => d.timestamp))]
	const timestamps_day = timestamps_.map((timestamp) => new Date(timestamp).toLocaleDateString())
	const timestamps_hours = timestamps_.map((timestamp) =>
		new Date(timestamp).toLocaleString(undefined, {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: 'numeric'
		})
	)
	const timestamps_hours_minutes = timestamps_.map((timestamp) =>
		new Date(timestamp).toLocaleString(undefined, {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: 'numeric',
			minute: '2-digit'
		})
	)
	const timestamps_full = timestamps_.map((timestamp) => new Date(timestamp).toLocaleString())
	const timestamps = timestamps_full
	//console.log("categories " + categories)
	//console.log("timestamps " + timestamps)
	const xScale = d3.scaleBand().domain(timestamps).range(range_x)
	// make a scale for each category
	const yScales = categories.reduce((scales, categoryName) => {
		scales[categoryName] = d3
			.scaleLinear()
			.domain(d3.extent(csv.map((d) => d[categoryName])))
			.range(range_y)
		return scales
	}, {})
	//console.log(yScales);
	const zScale = d3.scaleBand().domain(categories).range(range_z)

	onMount(() => {

	})

	function getPaletteColor(index) {
		const palette = $PAR.theme === 'dark'? IBM_palette_dark : IBM_palette_light
		const maxIndex = palette.length - 1
		if (index < 0) {
			index = maxIndex // Wrap to the last color if the index is negative
		} else if (index > maxIndex) {
			index = index % (maxIndex + 1) // Wrap to the first color if the index is too large
		}
		return palette[index]
	}

	const verticesP = [];
	//const vertices = {};
	const points3d = {};
	const points2d = {};
	const colors = [];
	const geometry = new PlaneGeometry(10, 10, 30, 30)
	function updatePoints() {
		csv.forEach((d, t) => {
			//points3d[cat] = []
			categories.forEach((cat, i) => {
				const x = xScale(timestamps[t])	
				const y = yScales[cat](d[cat])
				const z = zScale(categories[i])
				verticesP.push(x, y, z)
				const c = (y+0.01)/range_y[1]*360
				const color = hsv2rgb(c, 0.8, 1)
				colors.push(...color)
			});
		});
		// Construct the points3d points2d array by categories
		
		categories.forEach((cat, i) => {
			points2d[cat] = []
			points3d[cat] = []
			csv.forEach((d, t) => {
				const x = xScale(timestamps[t])	
				const y = yScales[cat](d[cat]) == 0 ? 0.01 : yScales[cat](d[cat])
				const z = zScale(categories[i])		
				points2d[cat] = [new Vector2(x, y), ...points2d[cat]]
				points3d[cat] = [new Vector3(x, y, z), ...points3d[cat]]

			})
		});		
		
		//categories.forEach((cat, i) => {
		const cat = "Temperature"
		const vertices = geometry.getAttribute('position').array
		// Iterate through each line segment
		const np = points3d[cat].length;
		for (let i = 0, v = 0, n = np; i < np - 1; i++, v += 3, n-= 3) {
			const point1 = points3d[cat][i];
			const point2 = points3d[cat][i + 1];
			// Interpolate additional points between point1 and point2
			const numInterpolatedPoints = 10; // Adjust as needed
			// for (let j = 0; j < numInterpolatedPoints; j++) {
			// 	const alpha = j / numInterpolatedPoints;
			// 	const interpolatedPoint = {
			// 		x: point1.x + alpha * (point2.x - point1.x),
			// 		y: point1.y + alpha * (point2.y - point1.y),
			// 		z: point1.z + alpha * (point2.z - point1.z),
			// 	};

			// 	// Assign interpolated point values to the vertices array by index
			// 	vertices[v] = interpolatedPoint.x;
			// 	vertices[v + 1] = interpolatedPoint.y;
			// 	vertices[v + 2] = interpolatedPoint.z;
			// }
			const p = points3d[cat][i];
			vertices[n] = p.x;
			vertices[n+1] = p.y;
			vertices[n+2] = p.z;
		}
		// });	
		geometry.computeVertexNormals()
	}


	updatePoints()


	// points[cat] = [new Vector3(x, y, z), ...points[cat]]
	//$: console.log(points)

	const first_x = timestamps[0]
	const last_x = timestamps[timestamps.length - 1]

	// Grid
	//const g_x = xScale(timestamps[timestamps.length - 1]) 
	const g_z = zScale(categories[categories.length - 1]) 
	//console.log(timestamps)
	
	if(browser) {
		$PAR = {
			pos1: {x:0, y:0, z:0},
			pos2: {x:0, y:1, z:0},
			pos3: {x:0.5, y:2, z:0},
			pos4: {x:0.5, y:0, z:0},
			theme: 'dark',
			bgColor: '#2b665b',
			fgColor: '#000000',
			shape: localStorage.shape ? localStorage.shape : 'lines',
			camera: localStorage.camera ? localStorage.camera : 'Perpective'
			// rotation: [x:0, y:0, z:0]
		}
		// console.log(JSON.stringify($PAR))
		const pane = new Pane({title: '3D graph control'})
		const panel = pane.addFolder({title: 'colors'})
		// panel.addBinding($PAR, 'pos1', {
		// 	label: 'Axis 1',
		// 	min: -20,
		// 	max: 20,
		// 	step: 0.1
		// }).on('change', ({value}) => {
		// 	$PAR.pos1 = value
		// });
		// panel.addBinding($PAR, 'pos2', {
		// 	label: 'Axis 2',
		// 	min: -20,
		// 	max: 20,
		// 	step: 0.1
		// }).on('change', ({value}) => {
		// 	$PAR.pos2 = value
		// });
		// panel.addBinding($PAR, 'pos3', {
		// 	label: 'Axis 3',
		// 	min: -20,
		// 	max: 20,
		// 	step: 0.1
		// }).on('change', ({value}) => {
		// 	$PAR.pos3 = value
		// });
		// panel.addBinding($PAR, 'pos4', {
		// 	label: 'Axis 4',
		// 	min: -20,
		// 	max: 20,
		// 	step: 0.1
		// }).on('change', ({value}) => {
		// 	$PAR.pos4 = value
		// });						
		// panel.addBinding( $PAR, 'theme', {
		// 	options: {Dark: 'dark', Light: 'light'}
		// }).on('change', ({value}) => {
		// 	$PAR.theme = value
		// });	
		panel.addBinding( $PAR, 'shape', { //Area: 'area',
			options: {Points: 'points', Lines: 'lines', Area: 'area', Bar: 'bar', Cone: 'cone' }
		}).on('change', ({value}) => {
			$PAR.shape = value
			localStorage.setItem('shape', value)
		});
		panel.addBinding( $PAR, 'camera', {
			options: {Perpective: 'Perpective', Ortographic: 'Orto'}
		}).on('change', ({value}) => {
			$PAR.camera = value
			localStorage.setItem('camera', value)
		});	
		
		panel.addBinding($PAR, 'bgColor').on('change', ({value}) => {
			$PAR.bgColor = value
		});
		
		panel.addBinding($PAR, 'fgColor').on('change', ({value}) => {
			$PAR.fgColor = value
		});
		// pane.addBinding(PAR, 'latest', 
		// 	{min: 0, max: 100, step: 1});
		// pane.addBinding(PAR, 'offset', {
		// 	picker: 'inline',
		// 	expanded: true,
		// });			
	}
	// let v = [
	// 	$PAR.pos1.x, $PAR.pos1.y, $PAR.pos1.z, 
	// 	$PAR.pos2.x, $PAR.pos2.y, $PAR.pos2.z, 
	// 	$PAR.pos3.x, $PAR.pos3.y, $PAR.pos3.z, 
	// 	$PAR.pos4.x, $PAR.pos4.y, $PAR.pos4.z, 
	// ]



</script>

<!-- <Title /> -->
<Grid z={g_z/2} size={range_x[1]*2}/>
<!-- <T.AxesHelper args={[10]} position.x={$PAR.position.x} position.y={$PAR.position.y} position.z={$PAR.position.z}/>  -->

<!-- <Floor /> -->
{#if $PAR.camera === 'Perpective'}
	<CameraPerpective />
{:else if $PAR.camera === 'Orto'}
	<CameraOrto />
{/if}
<Light />

{#each csv as d, t}
	{#each categories as cat, i}
	<!-- {#key $PAR.theme} -->
		{#if $PAR.shape === 'bar'}
			<Bar
				{i}
				value={d[cat]}
				x={xScale(timestamps[t])}
				y={yScales[cat](d[cat])}
				z={zScale(categories[i])}
				color={getPaletteColor(i)}
			/>
		{:else if $PAR.shape === 'cone'}
			<Cone
				{i}
				value={d[cat]}
				x={xScale(timestamps[t])}
				y={yScales[cat](d[cat])}
				z={zScale(categories[i])}
				color={getPaletteColor(i)}
			/>
		{/if}
	<!-- {/key}	 -->
	{/each}
{/each}
{#if $PAR.shape === 'points'}
	<Point vertices={verticesP} {colors} />
{:else if $PAR.shape === 'lines'}
	{#each categories as cat, i}
		<Line points3d={points3d[cat]} color={getPaletteColor(i)} />
	{/each}
{:else if $PAR.shape === 'area'}

<!-- {@const v = [0,0,0,  0,1,0,  0.5,2,0, 0.5,0,0] }  -->
<!-- {@const v = [$PAR.pos1, $PAR.pos2, $PAR.pos3, $PAR.pos4] } -->
<!-- {@debug v} -->
	<!-- {#key v} -->
		<T.Mesh  rotation.x={DEG2RAD * - 90}  {geometry}   >
			<T.MeshBasicMaterial wireframe={true} /> 		
		</T.Mesh>
		<!-- 
			{#each categories as cat, i}
				<Area  vertices={vertices[cat]} points2d={points2d[cat]} points3d={points3d[cat]} color={getPaletteColor(i)} />
			{/each} -->
	<!-- {/key}		 -->
{/if}	

<XLabels text={last_x} x={range_x[0] - 0.5} z={-range_z[1]/2 + 0.3} color={$PAR.bgColor}/>
<XLabels text={first_x} x={range_x[1] + 0.1} z={-range_z[1]/2 + 0.3} color={$PAR.bgColor}/>

<!-- 
{#each timestamps as d, i} 
{console.log(xScale(d))}
	<XLabels {d} x={xScale(d)} y=0 z={0}/>
{/each} -->

{#each categories as text, i}
	<!-- {console.log(zScale(text))} -->
	<CatLabels {text} x={range_x[1]} y={0.01} z={zScale(text)} color={getPaletteColor(i)}/>
{/each}

