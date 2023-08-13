// YourSvelteComponent.svelte
<script lang="ts">
  import { writable, get } from 'svelte/store';
  import { onMount } from 'svelte';
  // import { io } from 'socket.io-client'
  // import {browser} from '$app/environment';

  const wsMessages = writable([]);

  let ws;
  const connectWebSocket = () => {
      ws = new WebSocket('ws://localhost:8765'); // Replace with your WebSocket server URL
      ws.addEventListener("open", (event: any) => {
        console.log("connected to WebSocket server")
      });
      ws.addEventListener("close", (event: any) => {
        console.log("WebSocket connection closed")
      });                
      ws.addEventListener("message", (event: any) => {        
        const message: Request = JSON.parse(event.data);
        console.log("new ws message" + {message})
        // if (message.device === "" ) {
        //   
        // }
        wsMessages.update((messages) => [...messages, message]);
        
      });
    };

  onMount(connectWebSocket);
</script>

<h1>WebSocket Messages:</h1>
<ul>
  {#each $wsMessages as message}
    <li>{JSON.stringify( message)}</li>
  {/each}
</ul>
