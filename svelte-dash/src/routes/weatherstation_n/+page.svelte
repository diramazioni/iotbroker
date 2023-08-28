<script lang="ts">
  import { base } from "$app/paths"
  import { onMount } from 'svelte';
	import type { PageData } from './$types'
  import { invalidate, invalidateAll } from '$app/navigation';
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from '$lib/options'
  //import {device_selected} from '$lib/stores'
  import { page } from '$app/stores';
  import { writable } from 'svelte/store';

  import Slider from '@bulatdashiev/svelte-slider';
  

  export let data: PageData
  $: ({ devices, device_type, device_selected } = data)
  $: device_data = []
  const max = Number(data.range[1] - data.range[0])
  let range_slider = [0,max]
  let calibrated = true

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
    //refresh_data(device_type, edata.device)
    fetch_data();
  }

  const refresh_data = async (device_type: String, device_selected: String) => {
      console.log(`refresh_data ${base}/api/${device_type}/${device_selected}`)
      const url = `${base}/api/${device_type}/${device_selected}`;
      //invalidate(url);
      //invalidate(`${base}/${device_type}/`);
      //invalidate();
  }


  export const fetch_data = async () => {
    data.device_selected = device_selected //set and update doesn't work why?
    extOptions = { ...options,  title: `${device_selected}` }
    const url = `${base}/api/${device_type}/${device_selected}`;
    console.log(`fetch_data ${url}`)
    const response = await fetch(url)
    device_data = await response.json();
    return device_data
  }

  let extOptions = { ...options }
  onMount(() => {
    // Establish WebSocket connection when component mounts
    const ws = new WebSocket('ws://localhost:8765');
    ws.addEventListener('message', handleWebSocketMessage);
    // Update the store with WebSocket connection
    websocket.set(ws);    
    fetch_data() 
    
  });
</script>
<h2>Devices</h2>

<select bind:value={device_selected} on:change={() => (fetch_data())} >
  {#each devices as device, index}
      <option value={device}>
        {device}
      </option>
  {/each}
</select>

<!--
{range_slider[0]},{range_slider[1]}    -->
<Slider step="10" max={Number(max)} bind:value={range_slider} range order />
<!-- <pre>
  {JSON.stringify(device_data)}
</pre> -->

<AreaChart data={device_data} options={extOptions} style="padding:2rem;" />

<style>
  h2, select, input {
    margin-left: 1rem;
  }

</style>