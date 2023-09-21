<script lang="ts">
	// Svelte
	import { base } from '$app/paths'
	import { onMount, afterUpdate, beforeUpdate, getContext } from 'svelte'
	import type { PageData } from './$types'
	import { browser } from '$app/environment';
	// Installed
	import { Canvas } from '@threlte/core'
	import * as d3 from 'd3'
	// Local
	import { PAR, socketStore } from '$lib/stores'
	import Scene from '$lib/threlte/Scene.svelte'
	import { fetch_CSV, sliceCsv } from '$lib/shared'

	export let data: PageData

	$: ({ devices, device_type, device_csv, categories, max_lines } = data)
	
	$: category_on = []
	let device_selected = ""
	let max_data = 30
	// $: sliced_csv = sliceCsv(device_csv, max_data)
	let sliced_csv = ""
	// let csv_data = []

	const update_data = async () => {
		//data.device_selected = device_selected
		console.log("device_selected " + device_selected)
		console.log("device_type " + device_type)
		console.log("category_on " + category_on)
		device_csv = await fetch_CSV(fetch, device_type, device_selected, category_on)		// data.device_selected = device_selected		
		sliced_csv = sliceCsv(device_csv, max_data)
		device_csv = sliced_csv
	}

	async function handleWebSocketMessage(event) {
		const edata = JSON.parse(event.data)
		if (edata.device === device_selected) {
			// console.log("WS: Update " + device_type +"/"+ device_selected)
			update_data()
		} else {
			// console.log("WS: Ignoring message " + edata.device )
		}
	}

	onMount(() => {
		const ws = new WebSocket('ws://localhost:8765')
		ws.addEventListener('message', handleWebSocketMessage)
		// Update the socket store in the context with WebSocket connection
		$socketStore = ws
		category_on = categories
		device_selected = devices[0]
	})

</script>

<h2>Devices</h2>
<select bind:value={device_selected} on:change={() => update_data()}>
	{#each devices as device, index}
		<option value={device}>
			{device}
		</option>
	{/each}
</select>

<div style="margin-top: 20px; width: 85vw;">
	<button on:click={() => category_on=[]}> Unselect </button>
	{#each categories as category}
		<label style="margin: 0.5rem;">
			<input type="checkbox" bind:group={category_on} 
			value={category} on:change={() => update_data()}/>
			{category}
		</label>
	{/each}
</div>

{#if browser}
	<label style="margin-top: 20px; width: 40vw;">
		<input type="number" bind:value={max_data} min="1" max={max_lines} on:change={() => update_data()}/>
		<input type="range" bind:value={max_data} min="1" max={max_lines} on:change={() => update_data()}/>
		show last {max_data} data
	</label>		
{/if}

<div class="canvas-wrapper" 
	style="background-image: radial-gradient({$PAR.bgColor} 0%, {$PAR.fgColor} 100%)">
	<Canvas>
		{#key sliced_csv}
		<!-- {console.log(category_on)} -->
			<Scene csv_data={device_csv} categories={category_on}/>
		{/key}
	</Canvas>
</div>

<style>
	button {
		margin-left: 1rem;
		padding: .3rem;
		background-color: #ccc;
	}
	button:hover {
		background-color: #9298c8;
	}
	input[type=number] {
		width: 3rem;
	}
	h2, select {
		margin-left: 1rem;
	}
	.canvas-wrapper {
		/* position: fixed; */
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
	}
</style>
