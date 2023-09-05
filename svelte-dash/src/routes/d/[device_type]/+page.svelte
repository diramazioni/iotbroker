<script lang="ts">
	import { base } from "$app/paths"
  import { onMount, getContext } from 'svelte';
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  //import { page } from '$app/stores';
  import { writable } from 'svelte/store';
  import { fetch_data, fetch_opt } from '$lib/shared';


  export let data: PageData
  $: ({ devices, device_type, device_selected, device_data, device_opt } = data) 
  
  let calibrated = true 
  const socketStore = writable(null);
  
  const update_data = async () => {
    data.device_selected = device_selected
    device_data = await fetch_data(fetch, device_type, device_selected);
    device_opt = await fetch_opt(fetch, device_type, device_selected);
  }
  
  async function handleWebSocketMessage(event) {
    const edata = JSON.parse(event.data);
    if (edata.device === device_selected) {
      console.log("WS: Update " + device_type +"/"+ device_selected)
      update_data()
    } else {
      console.log("WS: Ignoring message " + edata.device )
    }
  }
  
  onMount(() => {
  
    const ws = new WebSocket('ws://localhost:8765');
    ws.addEventListener('message', handleWebSocketMessage);
    // Update the socket store in the context with WebSocket connection
    $socketStore = ws;

  });
</script>
<h2>Devices</h2>

<select bind:value={device_selected} on:change={() => (update_data())} >
  {#each devices as device, index}
      <option value={device}>
        {device}
      </option>
  {/each}
</select>

  {#if device_type !== 'etrometer'} 
    <AreaChart data={device_data} options={device_opt} style="padding:2rem;" />
  {:else}
    <input type="checkbox" bind:checked={calibrated}> calibrated
    <LineChart data={device_data.CO2} options={device_opt.CO2} style="padding:2rem; flex:1;" />
    <LineChart data={device_data.TC} options={device_opt.TC} style="padding:2rem; flex:1;" />
    <LineChart data={device_data.RH} options={device_opt.RH} style="padding:2rem; flex:1;" />
  {/if}



<style>
  h2, select {
    margin-left: 1rem;
  }

</style>