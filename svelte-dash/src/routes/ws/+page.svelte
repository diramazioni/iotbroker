<script lang="ts">
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from './options'

  export let data: PageData
  $: ({ weatherstation, weatherstation_virt, etrometer } = data)
  const weatherstationdOptions = { ...options,  title: "Weather Stations" }
  const weatherstation_virtOptions = { ...options,  title: "Virtual Weather Stations" }
  const etrometerOptionsCO2 = { ...options,  title: "ETRometer CO2", }
  const etrometerOptionsTC = { ...options,  title: "ETRometer TC", }
  const etrometerOptionsRH = { ...options,  title: "ETRometer RH", }

</script>

<AreaChart data={weatherstation} options={weatherstationdOptions} style="padding:2rem;" />

<!-- <AreaChart data={weatherstation_virt} options={weatherstation_virtOptions} style="padding:2rem;" />
<div class="devices">
    <LineChart data={etrometer.CO2} options={etrometerOptionsCO2} style="padding:2rem; flex:1;" />
    <LineChart data={etrometer.TC} options={etrometerOptionsTC} style="padding:2rem; flex:1;" />
    <LineChart data={etrometer.RH} options={etrometerOptionsRH} style="padding:2rem; flex:1;" />
</div> -->

<style>

  .devices  {
    display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  }
  .devices > * {
    background: #eee;
    display: flex;
    flex: 1;
  }
  /* }
  .devices div div {
    flex: 1;
    border: 1px solid #ccc;
    padding: 5px;
    width: 50px;
    overflow-x: auto;
  } */
</style>