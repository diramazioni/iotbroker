<script lang="ts">
	import { base } from '$app/paths'
	import { onMount, afterUpdate, getContext } from 'svelte'
	import type { PageData } from './$types'
	import { LineChart, AreaChart } from '@carbon/charts-svelte'
	import '@carbon/styles/css/styles.css'
	import '@carbon/charts-svelte/styles.css'
	import { DateInput } from 'date-picker-svelte'

	import { writable } from 'svelte/store'
	import { fetch_range, fetch_data, fetch_opt } from '$lib/shared'


	import { toast } from '@zerodevx/svelte-toast'
	import {breakpoints, mediaQueryStore } from '$lib/stores'
	//
	import { browser } from "$app/environment"
	import { PUBLIC_WS_HOST	} from '$env/static/public';

	export let data: PageData

	let chart: null | LineChart | AreaChart = null

	$: ({ devices, device_type, device_selected, device_data, device_opt } = data)
	$: selectedDevice = device_selected;

	$: domain_range = [new Date(), new Date()]

	let category_on: [] = []

	let calibrated = true
	const socketStore = writable(null)

	// match medium screen size and change chart options 
	let mediumScreen = mediaQueryStore(breakpoints["md"]);
	$: {		
		if($mediumScreen && device_opt?.legend) {
			device_opt.legend.position = "left"	
			device_opt.legend.orientation = "vertical"
			// console.log("medium screen")		
		} else if (device_opt?.legend){
			device_opt.legend.position = "bottom"	
			device_opt.legend.orientation = "horizontal"	
			// console.log("small screen")	
		}
		if (category_on.length && device_opt?.data) {
			device_opt['data']['selectedGroups'] = category_on
		}	
	}

	const update_data = async () => {
		//data.device_selected = device_selected
		console.log(selectedDevice)

		let ranges =  await fetch_range(fetch, device_type, selectedDevice);
  		ranges = ranges.slice(1)
  		domain_range = [new Date(ranges[0]), new Date(ranges[1])]
		//domain_range = [new Date(domain_range[0]), new Date(domain_range[1])]
		device_data = await fetch_data(fetch, device_type, selectedDevice, domain_range)
		device_opt = await fetch_opt(fetch, device_type, selectedDevice, domain_range)

		//device_opt.zoomBar.top.initialZoomDomain = domain_range
		if('category_on' in localStorage) {
			category_on = JSON.parse(localStorage.category_on); // init the category_on with previews settings
		}	

	}

	async function handleWebSocketMessage(event) {
		const edata = JSON.parse(event.data)
		if (edata.device === device_selected) {
			// toast notification
			toast.push('Update for <strong>'+edata.device+'</strong><br>'+
			JSON.stringify(edata.content, null, 2), {
				theme: {
					'--toastColor': 'mintcream',
					'--toastBackground': '#2F855A',
					'--toastBarBackground': 'rgba(72,187,120,0.9)'
				},
				duration: 2000,
				//initial: 0,
			})
			update_data()
		} else { // message on a different device
			toast.push('Update for <strong>'+edata.device+'</strong><br>'+
			JSON.stringify(edata.content, null, 2), {duration: 1000})
		}
	}

	async function handleNewRange(event) {
		localStorage.setItem('domain_range', JSON.stringify(domain_range))
		//localStorage.setItem('domain_end', domain_range[1].toLocaleString())
		console.log(`update ${domain_range}`)

		await update_data()
	}

	function legendOnclick(e: MouseEvent) {
		category_on = e.detail.dataGroups
			.filter((element) => element.status === 1)
			.map((element) => element.name)
		localStorage.setItem('category_on', JSON.stringify(category_on))
		if (category_on.length === 1) {
			device_opt.axes.left.title = category_on[0]
			delete device_opt.axes.right;
		} 
		// console.log(category_on);
	}
	
	function zoomDomainChange(e: MouseEvent) {
		domain_range = e.detail.newDomain
	}


	onMount(() => {
		if ('domain_range' in localStorage) {
			domain_range = JSON.parse(localStorage.domain_range);
			domain_range =  [new Date(domain_range[0]), new Date(domain_range[1])]
			//console.log(domain_range)
			//domain_range = [new Date(localStorage.domain_start),new Date(localStorage.domain_end)]
		
		} else {
			// if(device_opt) {
			// 	domain_range = device_opt.zoomBar.top.initialZoomDomain
			// 	domain_range = [new Date(domain_range[0]), new Date(domain_range[1])]
// }
		}
		if('category_on' in localStorage) {
			category_on = JSON.parse(localStorage.category_on); // init the category_on with previews settings
			//console.log(category_on);
		}
		//category_on = chart.model.allDataGroups // init the category_on on first update

		// Specify here where the websocket server is listening
		const ws = new WebSocket(PUBLIC_WS_HOST)
		console.log("WS CONNECT " + PUBLIC_WS_HOST)
		
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

<div class="ml-3  md:flex md:flex-row items-end">
	<div class="md:m-5" >
		<p class="-mt-2">Devices</p>
		<select bind:value={selectedDevice} on:change={() => update_data()} 
			class="-mt-1">
			{#each devices as device, index}
				<option  value={device}>
					{device}
				</option>
			{/each}
		</select>
	</div>
	<div class="md:m-5">
		<p class="md:-mt-2">Start</p>
		<DateInput id="start" bind:value={domain_range[0]}  dynamicPositioning={true} timePrecision={"minute"} browseWithoutSelecting={false} closeOnSelection={true} 
		on:select={handleNewRange} />
		<!-- <input type="text" bind:value={domain_range[0]} class="range text-2xl" on:change={() => update_data()}/> -->
	</div>
	<div class="md:m-5">
		<p class="md:-mt-2">End</p>
		<DateInput id="end" bind:value={domain_range[1]} dynamicPositioning={true} timePrecision={"minute"} browseWithoutSelecting={false} closeOnSelection={true} 
		on:select={handleNewRange} />
		<!-- <input type="text" bind:value={domain_range[1]} class="range text-2xl" on:change={() => update_data()}/> -->
	</div>
	<div class="md:m-5 items-center justify-center">
		<button class="button" on:click={handleNewRange}>Set</button>
	</div>
</div>


{#if device_type !== 'etrometer'}
	{#key device_opt}
	<AreaChart bind:chart data={device_data} options={device_opt} style="padding:2rem;" />
	{/key}
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
