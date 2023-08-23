<script lang="ts">
  import { onMount } from 'svelte';
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from '$lib/options'
  //import {device_selected} from '$lib/stores'
  import { page } from '$app/stores';

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
    extOptions = { ...options,  title: `${device_selected}` }
    const url = `/api/${device_type}/${device_selected}`;
    console.log(url)
    const response = await fetch(url)
    device_data = await response.json();
    return device_data
  }

  let extOptions = { ...options }
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