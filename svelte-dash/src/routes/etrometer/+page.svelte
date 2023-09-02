<script lang="ts">
  import { base } from "$app/paths"
  import { getContext, onMount } from 'svelte';
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from '$lib/options'
  import { page } from '$app/stores';
  import Pre from '$lib/pre.svelte'

  export let data: PageData
  $: ({ devices, device_type, device_selected } = data) //, device_data 
  const socketContext = getContext('socket-context');
  $: device_data = socketContext.device_data
  

  let calibrated = true

  let etrometerOptionsCO2 = { ...options }
  let etrometerOptionsTC = { ...options }
  let etrometerOptionsRH = { ...options }

  const update_data = async () => {
    data.device_selected = device_selected
    await socketContext.fetch_data(device_type, device_selected)
    etrometerOptionsCO2 = { ...options,  title: `${device_selected} CO2` }
    etrometerOptionsTC = { ...options,  title: `${device_selected} TC` }
    etrometerOptionsRH = { ...options,  title: `${device_selected} RH` }
  }  
  // export const fetch_data = async () => {
  //   data.device_selected = device_selected //set and update doesn't work why?

  //   const url = `${base}/api/${device_type}/${device_selected}`;
  //   console.log(url)
  //   const response = await fetch(url)
  //   device_data = await response.json();
  //   return device_data
  // }


  onMount(() => {
    $device_data = null
    update_data()
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
<input type="checkbox" bind:checked={calibrated}> calibrated

{#if $device_data} 

  <LineChart data={$device_data.CO2} options={etrometerOptionsCO2} style="padding:2rem; flex:1;" />
  <LineChart data={$device_data.TC} options={etrometerOptionsTC} style="padding:2rem; flex:1;" />
  <LineChart data={$device_data.RH} options={etrometerOptionsRH} style="padding:2rem; flex:1;" />

{/if}


<style>
  h2, select, input {
    margin-left: 1rem;
  }

</style>