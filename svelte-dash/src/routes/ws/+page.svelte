<script lang="ts">
	import type { PageData } from './$types'
  import { LineChart } from '@carbon/charts-svelte'
  import '@carbon/styles/css/styles.css'
  import '@carbon/charts-svelte/styles.css'
  import options from './options'
  import data from './data'
  // type DataRecord = { x: number, y: number }
  // export let data: DataRecord[] = [
  //   { x: 0, y: 0 },
  //   { x: 1, y: 2 },
  //   { x: 2, y: 1 },
  // ]
  // const x = (d: DataRecord) => d.x
  // const y = (d: DataRecord) => d.y

</script>


<LineChart {data} {options} style="padding:2rem;" />

<!-- 
  <h1>weather stations</h1>
<div class="devices">
  <div>
    <div>name</div>
    <div>timestamp</div>
    <div>Battery_Voltage</div>
    <div>Temperature</div>
    <div>Pressure</div>
    <div>Humidity</div>
    <div>GasResistance</div>
    <div>Altitude</div>
    <div>Ts_1</div>
    <div>Ts_2</div>
    <div>Ts_3</div>
    <div>Us_1</div>
    <div>Us_2</div>
    <div>Us_3</div>
    <div>W_vel</div>
    <div>W_dir</div>
  </div>  
{#each device as ws}
<div>
  <div>
    {ws.name}
  </div>  
  <div>
    {ws.timestamp}
  </div>  
  <div>
    {ws.Battery_Voltage}
  </div>  
  <div>
    {ws.Temperature}
  </div>  
  <div>
    {ws.Pressure}
  </div>  
  <div>
    {ws.Humidity}
  </div>  
  <div>
    {ws.GasResistance}
  </div>  
  <div>
    {ws.Altitude}
  </div>        
  <div>
    {ws.Ts_1}
  </div>   
  <div>
    {ws.Ts_2}
  </div>   
  <div>
    {ws.Ts_3}
  </div>   
  <div>
    {ws.Us_1}
  </div>   
  <div>
    {ws.Us_2}
  </div>   
  <div>
    {ws.Us_3}
  </div>   
  <div>
    {ws.W_vel}
  </div>   
  <div>
    {ws.W_dir}
  </div>                 
</div>
{/each}
  
</div>
 -->


<style>

  .devices  {
    display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  }
  .devices div {
    background: #eee;
    display: flex;
  }
  .devices div div {
    flex: 1;
    border: 1px solid #ccc;
    padding: 5px;
    width: 50px;
    overflow-x: auto;
  }
</style>