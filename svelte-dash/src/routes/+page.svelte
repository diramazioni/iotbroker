<script lang="ts">
	import type { PageData } from './$types'

	export let data: PageData

	$: ({ devices } = data)
</script>

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
{#each devices as device}
<div>
  <div>
    {device.name}
  </div>  
  <div>
    {device.timestamp}
  </div>  
  <div>
    {device.weatherStation.Battery_Voltage}
  </div>  
  <div>
    {device.weatherStation.Temperature}
  </div>  
  <div>
    {device.weatherStation.Pressure}
  </div>  
  <div>
    {device.weatherStation.Humidity}
  </div>  
  <div>
    {device.weatherStation.GasResistance}
  </div>  
  <div>
    {device.weatherStation.Altitude}
  </div>        
  <div>
    {device.weatherStation.Ts_1}
  </div>   
  <div>
    {device.weatherStation.Ts_2}
  </div>   
  <div>
    {device.weatherStation.Ts_3}
  </div>   
  <div>
    {device.weatherStation.Us_1}
  </div>   
  <div>
    {device.weatherStation.Us_2}
  </div>   
  <div>
    {device.weatherStation.Us_3}
  </div>   
  <div>
    {device.weatherStation.W_vel}
  </div>   
  <div>
    {device.weatherStation.W_dir}
  </div>                 
</div>
{/each}
  
</div>

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