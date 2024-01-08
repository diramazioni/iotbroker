<script lang="ts">
	import { base } from '$app/paths'
	import { onMount, afterUpdate, getContext } from 'svelte'
	import type { PageData } from './$types'
	import { LineChart, AreaChart } from '@carbon/charts-svelte'
	import '@carbon/styles/css/styles.css'
	import '@carbon/charts-svelte/styles.css'
	import { DateInput } from 'date-picker-svelte'

	import { writable } from 'svelte/store'
	import { fetch_data, fetch_opt } from '$lib/shared'

	import { toast } from '@zerodevx/svelte-toast'

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
		domain_range = [new Date(domain_range[0]), new Date(domain_range[1])]
		device_data = await fetch_data(fetch, device_type, device_selected, domain_range)
		device_opt = await fetch_opt(fetch, device_type, device_selected, domain_range)
		//device_opt.zoomBar.top.initialZoomDomain = domain_range
		console.log(`update ${domain_range}`)
	}

	async function handleWebSocketMessage(event) {
		const edata = JSON.parse(event.data)
		if (edata.device === device_selected) {
			// console.log("WS: Update " + device_type +"/"+ device_selected)
			toast.push('Update for <strong>'+edata.device+'</strong><br>'+
			JSON.stringify(edata.content, null, 2), {
				theme: {
					'--toastColor': 'mintcream',
					'--toastBackground': '#2F855A',
					'--toastBarBackground': 'rgba(72,187,120,0.9)'
				},
				initial: 0,
			})
			update_data()
		} else {
			toast.push('Update for <strong>'+edata.device+'</strong><br>'+
			JSON.stringify(edata.content, null, 2))
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
		
		// Specify here where the websocket server is listening
		const ws = new WebSocket('wss://greenlab.unibo.it/ws:443')
		//const ws = new WebSocket('ws://localhost:8765')
		
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

<!-- <button on:click={() => toast.push('New message from <strong>'+device_selected+'</strong><br>')}>SHOW TOAST</button>
<button on:click={() => 			toast.push('Update for <strong>'+device_selected+'</strong><br>', {
	theme: {
		'--toastColor': 'mintcream',
		'--toastBackground': '#2F855A',
		'--toastBarBackground': 'rgba(72,187,120,0.9)'
	},
	initial: 0,
})}>SHOW TOAST2</button> -->

<h2>Devices</h2>

<div class="flex m-5 w-2/4">
	<div class="flex-1" >
		<select bind:value={device_selected} on:change={() => update_data()} class="devices">
			{#each devices as device, index}
				<option value={device}>
					{device}
				</option>
			{/each}
		</select>
	</div>
	<div class="flex-1">
		start
		<DateInput bind:value={domain_range[0]} closeOnSelection={true} dynamicPositioning={true} on:select={() => update_data()}/>
		<!-- <input type="text" bind:value={domain_range[0]} class="range text-2xl" on:change={() => update_data()}/> -->
	</div>
	<div class="flex-1">
		end
		<DateInput bind:value={domain_range[1]} closeOnSelection={true} dynamicPositioning={true} on:select={() => update_data()}/>
		<!-- <input type="text" bind:value={domain_range[1]} class="range text-2xl" on:change={() => update_data()}/> -->
	</div>
</div>


{#if device_type !== 'etrometer'}
	<AreaChart bind:chart data={device_data} options={device_opt} style="padding:2rem;" />
{:else}
	<input type="checkbox" bind:checked={calibrated} /> calibrated
	<LineChart data={device_data.CO2} options={device_opt.CO2} style="padding:2rem; flex:1;" />
	<LineChart data={device_data.TC} options={device_opt.TC} style="padding:2rem; flex:1;" />
	<LineChart data={device_data.RH} options={device_opt.RH} style="padding:2rem; flex:1;" />
{/if}
<!-- <div style="margin-left: 1rem; ">
	<a
		href={`${base}/api/csv/${device_type}/${device_selected}`}
		class="button"
		style="background-color: #ccc;"
	>
		get CSV
	</a>
</div> -->

<style>
	h2,
	select,
	.range {
		margin-left: 1rem;
	}
	:root {
		--toastContainerTop: auto;
		--toastContainerRight: auto;
		--toastContainerBottom: 8rem;
		--toastContainerLeft: calc(50vw - 8rem);
		--toastWidth: 100%;
    	--toastMinHeight: 2rem;
    	--toastPadding: 0 0.5rem;		
	  }
</style>
