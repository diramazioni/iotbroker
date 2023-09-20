<script lang="ts">
	import { base } from '$app/paths'
	import { onMount, afterUpdate, getContext } from 'svelte'
	import type { PageData } from './$types'
	import { LineChart, AreaChart } from '@carbon/charts-svelte'
	import '@carbon/styles/css/styles.css'
	import '@carbon/charts-svelte/styles.css'
	import { writable } from 'svelte/store'
	import { fetch_data, fetch_opt } from '$lib/shared'

	// import { browser } from "$app/environment"

	export let data: PageData

	let chart: null | LineChart | AreaChart = null

	$: ({ devices, device_type, device_selected, device_data, device_opt } = data)

	$: domain_range = [new Date(), new Date()]

	let category_on: [] = []

	let calibrated = true
	const socketStore = writable(null)

	const update_data = async () => {
		data.device_selected = device_selected
		device_data = await fetch_data(fetch, device_type, device_selected)
		device_opt = await fetch_opt(fetch, device_type, device_selected)
		if (domain_range.length) {
			// Change to selected zoom
			device_opt.zoomBar.top.initialZoomDomain = domain_range
		}
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

	function legendOnclick(e: MouseEvent) {
		category_on = e.detail.dataGroups
			.filter((element) => element.status === 1)
			.map((element) => element.name)
		// console.log(category_on);
	}
	function zoomDomainChange(e: MouseEvent) {
		domain_range = e.detail.newDomain
	}

	afterUpdate(() => {
		if (chart) category_on = chart.model.allDataGroups // init the category_on on first update
	})

	onMount(() => {
		domain_range = device_opt.zoomBar.top.initialZoomDomain
		domain_range = [new Date(domain_range[0]), new Date(domain_range[1])]
		const ws = new WebSocket('ws://localhost:8765')
		ws.addEventListener('message', handleWebSocketMessage)
		// Update the socket store in the context with WebSocket connection
		$socketStore = ws
		return () => {
			if (chart) chart.services.events.removeEventListener('legend-items-update', legendOnclick)
			if (chart) chart.services.events.removeEventListener('zoom-domain-change', zoomDomainChange)
		}
	})

	$: if (chart) chart.services.events.addEventListener('legend-items-update', legendOnclick)
	$: if (chart) chart.services.events.addEventListener('zoom-domain-change', zoomDomainChange)
</script>

<h2>Devices</h2>

<select bind:value={device_selected} on:change={() => update_data()} class="devices">
	{#each devices as device, index}
		<option value={device}>
			{device}
		</option>
	{/each}
</select>
<div class="w-100 text-center">
	<label class="ml-3">
		start
		<input type="text" bind:value={domain_range[0]} class="range text-2xl" />
	</label>
	<label class="ml-3">
		end
		<input type="text" bind:value={domain_range[1]} class="range text-2xl" />
	</label>
</div>


{#if device_type !== 'etrometer'}
	<AreaChart bind:chart data={device_data} options={device_opt} style="padding:2rem;" />
{:else}
	<input type="checkbox" bind:checked={calibrated} /> calibrated
	<LineChart data={device_data.CO2} options={device_opt.CO2} style="padding:2rem; flex:1;" />
	<LineChart data={device_data.TC} options={device_opt.TC} style="padding:2rem; flex:1;" />
	<LineChart data={device_data.RH} options={device_opt.RH} style="padding:2rem; flex:1;" />
{/if}
<div style="margin-left: 1rem; ">
	<a
		href={`${base}/api/csv/${device_type}/${device_selected}`}
		class="button"
		style="background-color: #ccc;"
	>
		get CSV
	</a>
</div>

<style>
	h2,
	select,
	.range {
		margin-left: 1rem;
	}
</style>
