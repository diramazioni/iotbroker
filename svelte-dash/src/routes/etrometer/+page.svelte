<script lang="ts">
  import { base } from "$app/paths"
  import { onMount } from 'svelte';
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from '$lib/options'
  //import {device_selected} from '$lib/stores'
  import { page } from '$app/stores';
  import Pre from '$lib/pre.svelte'
  import Slider from '@bulatdashiev/svelte-slider';
	
  //const device_type = 'weatherstation_v'
   
  export let data: PageData
  $: ({ devices, device_type, device_selected } = data)
  $: device_data = []
  const max = Number(data.range[1] - data.range[0])
  let range_slider = [0,max]
  let calibrated = true

  export const fetch_data = async () => {
    data.device_selected = device_selected //set and update doesn't work why?
    etrometerOptionsCO2 = { ...options,  title: `${device_selected} CO2` }
    etrometerOptionsTC = { ...options,  title: `${device_selected} TC` }
    etrometerOptionsRH = { ...options,  title: `${device_selected} RH` }
    const url = `${base}/api/${device_type}/${device_selected}`;
    console.log(url)
    const response = await fetch(url)
    device_data = await response.json();
    return device_data
  }

  let etrometerOptionsCO2 = { ...options }
  let etrometerOptionsTC = { ...options }
  let etrometerOptionsRH = { ...options }
  onMount(() => {
    //device_selected = (device_selected.length === 0 ) ? devices.sort()[0] : device_selected
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
<input type="checkbox" bind:checked={calibrated}> calibrated
<!--
{range_slider[0]},{range_slider[1]}    -->
<Slider step="10" max={Number(max)} bind:value={range_slider} range order />

<!-- <Pre name="device_data" value={device_data} /> -->
<div class="devices">
  <LineChart data={device_data.CO2} options={etrometerOptionsCO2} style="padding:2rem; flex:1;" />
  <LineChart data={device_data.TC} options={etrometerOptionsTC} style="padding:2rem; flex:1;" />
  <LineChart data={device_data.RH} options={etrometerOptionsRH} style="padding:2rem; flex:1;" />
</div> 

<style>
  h2, select, input {
    margin-left: 1rem;
  }

</style>