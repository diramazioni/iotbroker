<script lang="ts">
	import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import type { LayoutData } from './$types'
  import { page } from '$app/stores';
  //import {device_type, device_selected} from '$lib/stores'
  import Pre from '$lib/pre.svelte'

  export let data;

  $: device_data = []

  // Set up a writable store for WebSocket connection
  const websocket = writable(null);
  /*
    function handleWebSocketMessage(event) {
      const edata = JSON.parse(event.data);
      if (edata.device.includes('WeatherStation_n')) {
        console.log('WeatherStation_n')
        refreshWeatherStation_n(); // Trigger data refresh when 'data-refresh' message received
      } else if (edata.device.includes('WeatherStation_v')) {
        console.log('WeatherStation_v')
        refreshWeatherStation_v(); // Trigger data refresh when 'data-refresh' message received
      } else if (edata.device.includes('ETRometer')) {
        console.log('ETRometer')
        refreshETRometer(); // Trigger data refresh when 'data-refresh' message received
      } else if (edata.device.includes('Camera')) {
        console.log('Camera')
        refreshCamera(); // Trigger data refresh when 'data-refresh' message received
      } else {
        console.log('Unknown device')
      }
    }

    onMount(() => {
      // Establish WebSocket connection when component mounts
      const ws = new WebSocket('ws://localhost:8765');
      ws.addEventListener('message', handleWebSocketMessage);
      // Update the store with WebSocket connection
      websocket.set(ws);
    });
    
    // Functions to refresh data 
    async function refreshWeatherStation_n() {
      const response = await fetch('/api/weatherstation_n')
      const newData = await response.json();
      // weatherstation_n = newData;
    }
    async function refreshWeatherStation_v() {
      const response = await fetch('/api/weatherstation_v')
      const newData = await response.json();
      // weatherstation_v = newData;
    }
    async function refreshETRometer() {
      const response = await fetch('/api/etrometer')
      const newData = await response.json(); 
      // etrometer = newData;
    }  
    async function refreshCamera() {
      // Fetch data from the server and update as needed
    }

  */
</script>

<nav>
	<a href="/">home</a>
	<a href="/weatherstation_n">Weather Stations</a>
  <a href="/weatherstation_v">Virtual Weather Stations</a>
  <a href="/etrometer">Etrometers</a>
  <a href="/camera">Cameras</a>
</nav>

<slot />

<Pre name="export let data" value={data} />
<Pre name="device_type" value={$page.data.device_type} />
<Pre name="device_selected" value={$page.data.device_selected} />
<style>
			body {
				--bg-1: hsl(0, 0%, 100%);
				--bg-2: hsl(206, 20%, 90%);
				--bg-3: hsl(206, 20%, 80%);
				--fg-1: hsl(0, 0%, 13%);
				--fg-2: hsl(0, 0%, 20%);
				--fg-2: hsl(0, 0%, 30%);
				--link: hsl(208, 77%, 47%);
				--link-hover: hsl(208, 77%, 55%);
				--link-active: hsl(208, 77%, 40%);
				--border-radius: 4px;
				--font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
					'Open Sans', 'Helvetica Neue', sans-serif;
				--font-mono: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas,
					'DejaVu Sans Mono', monospace;
				background: var(--bg-1);
				color: var(--fg-1);
				font-family: var(--font);
				line-height: 1.5;
				margin: 1rem;
				height: calc(100vh - 2rem);
			}  
  			nav {
				position: relative;
				display: flex;
				gap: 1em;
				padding: 1em;
				background: var(--bg-2);
				z-index: 2;
				margin: 0 0 1em 0;
				border-radius: var(--border-radius);
			}
			nav a {
				text-decoration: none;
			}

			nav a[aria-current='true'] {
				border-bottom: 2px solid;
			}      
</style>