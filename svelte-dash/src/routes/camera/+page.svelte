
<script lang="ts">
	import { browser } from "$app/environment"
  import {onMount} from 'svelte';

    onMount(() => {
       //getElementById('imageCanvas');
       canvas = document.querySelector('canvas')
       ctx = canvas.getContext('2d');
    });
    let frame
    let ctx, canvas 

    let deviceName = "";
    const cam_devices = [
      "CAM-eli", "CAM-gv", "CAM-em", "CAM-poni"
    ]
		const host = "greenlab.unibo.it"; // Replace with the actual IP address or hostname
		const port = 443;
		const path_ws = "ws"
    const path = "cam"
    $: listing = `https://${host}/data/cam/${deviceName}`

    // if(browser) {
		//let deviceName = 'CAM-eli'; // Replace with the actual device name

    
    let ws;

    function initWebSocket() {

        const wsUrl = `wss://${host}:${port}/${path_ws}/${path}/${deviceName}`;

        ws = new WebSocket(wsUrl);

        ws.binaryType = 'arraybuffer';

        ws.onopen = function() {
            console.log('WebSocket connected');
            console.log({wsUrl});
        };

        ws.onmessage = function(event) {
            const imageBlob = new Blob([event.data], { type: 'image/jpeg' });
            const imageUrl = URL.createObjectURL(imageBlob);

            loadImage(imageUrl);
        };

        ws.onclose = function() {
            console.log('WebSocket closed');
        };
    }

    function loadImage(imageUrl) {
        const img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = imageUrl;
    }

    // Initialize WebSocket connection when the page loads
    window.onload = function() {
        //initWebSocket();
    };
    function handleSubmit() {
      initWebSocket();
      frame.src = listing;
    }
  
  //}

</script>

<form on:submit|preventDefault={handleSubmit} class="ml-5 ">
	<select	bind:value={deviceName} class="bg-zinc-200 p-1">
		<!-- on:change={() => (answer = '')} -->	
		{#each cam_devices as cam}
			<option value={cam}>
				{cam}
			</option>
		{/each}
	</select>


	<button type="submit" class="bg-zinc-200 hover:bg-zinc-300 ml-3 p-2 ">
		Set Cam
	</button>
</form>
<div class="flex items-center justify-center ">
  <canvas id="imageCanvas" width="800" height="600"></canvas> <!-- bind:this={canvas}  -->
</div>

<iframe bind:this={frame} src={listing} title="preview" class="w-full h-full"/>

<style lang="postcss">
  h1 {
    @apply m-4;
  }
  html, body {
      height: 100%;
      margin: 0;
      padding: 0;
  }
  
</style>