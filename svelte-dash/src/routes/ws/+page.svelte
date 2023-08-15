<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
	import type { PageData } from './$types'
  import { LineChart, AreaChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from './options'

  export let data: PageData
  $: ({ weatherstation_n, weatherstation_v, etrometer } = data)
  const weatherstationdOptions = { ...options,  title: "Weather Stations" }
  const weatherstation_virtOptions = { ...options,  title: "Virtual Weather Stations" }
  const etrometerOptionsCO2 = { ...options,  title: "ETRometer CO2", }
  const etrometerOptionsTC = { ...options,  title: "ETRometer TC", }
  const etrometerOptionsRH = { ...options,  title: "ETRometer RH", }

  // Set up a writable store for WebSocket connection
  const websocket = writable(null);
  function handleWebSocketMessage(event) {
    const data = JSON.parse(event.data);
    if (data.device.includes('WeatherStation_n')) {
      console.log('WeatherStation_n')
      refreshWeatherStation_n(); // Trigger data refresh when 'data-refresh' message received
    } else if (data.device.includes('WeatherStation_v')) {
      console.log('WeatherStation_v')
      refreshWeatherStation_v(); // Trigger data refresh when 'data-refresh' message received
    } else if (data.device.includes('ETRometer')) {
      console.log('ETRometer')
      refreshETRometer(); // Trigger data refresh when 'data-refresh' message received
    } else if (data.device.includes('Camera')) {
      console.log('Camera')
      refreshCamera(); // Trigger data refresh when 'data-refresh' message received
    } else {
      console.log('Unknown device')
    }
    // Update data or trigger data refresh here
  }

  onMount(() => {
    // Establish WebSocket connection when component mounts
    const ws = new WebSocket('ws://localhost:8765');
    ws.addEventListener('message', handleWebSocketMessage);
    
    // Update the store with WebSocket connection
    websocket.set(ws);
  });
  
  // Function to refresh data (fetch from the server again)
  async function refreshWeatherStation_n() {
    const response = await fetch('/api/weatherstation_n')
    const newData = await response.json();
    weatherstation_n = newData;
  }
  async function refreshWeatherStation_v() {
    const response = await fetch('/api/weatherstation_v')
    const newData = await response.json();
    weatherstation_v = newData;
  }
  async function refreshETRometer() {
    const response = await fetch('/api/etrometer')
    const newData = await response.json(); 
    etrometer = newData;
  }  
  async function refreshCamera() {
    // Fetch data from the server and update as needed
  }
</script>

<AreaChart data={weatherstation_n} options={weatherstationdOptions} style="padding:2rem;" />

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