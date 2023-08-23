<script lang="ts">
	import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import type { LayoutData } from './$types'
  import { page, navigating } from '$app/stores';
  //import {device_type, device_selected} from '$lib/stores'
  import Pre from '$lib/pre.svelte'

  export let data: LayoutData
  
  import "carbon-components-svelte/css/white.css";
  import '../app.css'

  $: ({ incoming } = data)

  import { Button, truncate, breakpoints } from "carbon-components-svelte";
  
  // Set up a writable store for WebSocket connection
  const websocket = writable(null);
  function handleWebSocketMessage(event) {
    const edata = JSON.parse(event.data);
    let device_type = ""
    if (edata.device.includes('WeatherStation_n')) {
      device_type = "weatherstation_n"
      console.log('WeatherStation_n')
    } else if (edata.device.includes('WeatherStation_v')) {
      device_type = "weatherstation_v"
      console.log('WeatherStation_v')
    } else if (edata.device.includes('ETRometer')) {
      device_type = "etrometer"
      console.log('etrometer')
    } else if (edata.device.includes('Camera')) {
      device_type = "camera"
      console.log('Camera')
    } else {
      console.log('Unknown device')
    }
    refresh_data(device_type, edata.device)
  }

  const refresh_data = async (device_type: String, device_selected: String) => {
      console.log(`refresh_data /api/${device_type}/${device_selected}`)
      const url = `/api/${device_type}/${device_selected}`;
      const res = await fetch(url);
      const inc = await res.json();
      incoming.push({[device_selected]: inc})
      
  }

  onMount(() => {
    // Establish WebSocket connection when component mounts
    const ws = new WebSocket('ws://localhost:8765');
    ws.addEventListener('message', handleWebSocketMessage);
    // Update the store with WebSocket connection
    websocket.set(ws);
  });
    

</script>

<nav class="w-full flex p-3 gap-2 justify-center items-center">
	<a class="hover:bg-blue-500 hover:text-white " href="/" aria-current={$page.url.pathname === "/"}>Home</a>
	<a class="hover:bg-blue-500 hover:text-white " href="/weatherstation_n" aria-current={$page.url.pathname === "/weatherstation_n"}>Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="/weatherstation_v" aria-current={$page.url.pathname === "/weatherstation_v"}>Virtual Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="/etrometer" aria-current={$page.url.pathname === "/etrometer"}>Etrometers</a>
  <a class="hover:bg-blue-500 hover:text-white " href="/camera" aria-current={$page.url.pathname === "/camera"}>Cameras</a>
</nav>

<slot />
<!-- 
<Pre name="export let data" value={data} />
<Pre name="page data" value={$page.data} /> -->



<style>
  			/* nav {
				position: relative;
				display: flex;
				gap: 1em;
				padding: 1em;
				background: var(--bg-2);
				z-index: 2;
				margin: 0 0 1em 0;
				border-radius: var(--border-radius);
			} */
			nav a {
				text-decoration: none;
			}

			nav a[aria-current='true'] {
				border-bottom: 2px solid;
			}      
</style>