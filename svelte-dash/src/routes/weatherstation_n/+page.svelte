<script lang="ts">
  import { base } from "$app/paths"
  import { onMount, getContext } from 'svelte';
	import type { PageData } from './$types'
  import { invalidate, invalidateAll } from '$app/navigation';
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from '$lib/options'
  //import {device_selected} from '$lib/stores'
  import { page } from '$app/stores';
  import { writable } from 'svelte/store';
  

  export let data: PageData
  $: ({ devices, device_type, device_selected } = data) //, device_data 
  const socketContext = getContext('socket-context');
  $: device_data = socketContext.device_data
  $: device_opt = socketContext.device_opt

  //const max = Number(data.range[1] - data.range[0])

  let calibrated = true 

  $: extOptions = {...options }
  const update_data = async () => {
    data.device_selected = device_selected
    await socketContext.fetch_data(device_type, device_selected)
    await socketContext.fetch_opt(device_selected)
  }

  
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

  {#if $device_data} 
  <!-- <pre>
    {JSON.stringify(extOptions)}
  </pre>   -->
  <AreaChart data={$device_data} options={$device_opt} style="padding:2rem;" />
  {/if}



<style>
  h2, select, input {
    margin-left: 1rem;
  }

</style>