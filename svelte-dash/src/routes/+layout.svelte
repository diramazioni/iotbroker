<script lang="ts">
  import { base } from "$app/paths";
	import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { setContext } from 'svelte';
  import type { LayoutData } from './$types'
  import { page } from '$app/stores';

  import "carbon-components-svelte/css/white.css";
  import '../app.css'

   import Pre from '$lib/pre.svelte'

  export let data: LayoutData

  $: ({ device_selected } = data)

  const socketStore = writable(null);
  const device_data = writable([]);
  const device_opt = writable([]);
  
  const fetch_data = async (device_type: string, device_selected: string) => {
    data.device_selected = device_selected //set and update doesn't work why?
    const url = `${base}/api/${device_type}/${device_selected}`;
    console.log(`fetch_data ${url}`)
    const response = await fetch(url)
    let json = await response.json()
    $device_data = json
    return json
  }

  const fetch_opt = async (device_selected: string, extra_title?:string) => {
    let url = `${base}/api/options/${device_selected}`;
    if (extra_title) {
      url = `?extra_title=${extra_title}`
    }
    console.log(`fetch_opt ${url}`)
    const response = await fetch(url)
    let json = await response.json()
    $device_opt = json
    return json
  }
  function handleWebSocketMessage(event) {
    const edata = JSON.parse(event.data);
    let device_type = $page.url.pathname.slice(1)
    if (edata.device === data.device_selected) {
      console.log("WS: Update " + data.device_selected)
      fetch_data(device_type, device_selected);
      fetch_opt(device_selected);
    } else {
      console.log("WS: Ignoring message " + edata.device )
    }
  }
  setContext('socket-context', {
    subscribe: socketStore,
    device_data: device_data,
    device_opt: device_opt,
    fetch_data,
    fetch_opt
  });


  onMount(() => {
    console.log()
    const ws = new WebSocket('ws://localhost:8765');
    ws.addEventListener('message', handleWebSocketMessage);
    // Update the socket store in the context with WebSocket connection
    $socketStore = ws;

  });
    

</script>

<nav class="w-full flex p-3 gap-2 justify-center items-center">
	<a class="hover:bg-blue-500 hover:text-white " href="{base}/" aria-current={$page.url.pathname === "/{base}/"}>Home</a>
	<a class="hover:bg-blue-500 hover:text-white " href="{base}/weatherstation_n" aria-current={$page.url.pathname === "/{base}/weatherstation_n"}>Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/weatherstation_v" aria-current={$page.url.pathname === "/{base}/weatherstation_v"}>Virtual Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/etrometer" aria-current={$page.url.pathname === "/{base}/etrometer"}>Etrometers</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/camera" aria-current={$page.url.pathname === "/{base}/camera"}>Cameras</a>
</nav>

<slot />
<!-- 
<Pre name="export let data" value={data} />
<Pre name="page data" value={$page.data} /> -->
<!-- <Pre name="incoming" value={incoming.length} /> -->



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