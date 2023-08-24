<script lang="ts">
  // import { Code, Notes, RevealJsContext, Slide } from '$lib';
  
  import Galery from "$lib/Gallery.svelte";
  const imageModules = import.meta.glob("$lib/assets/*.jpg"); 
  //const imagePath = Object.keys(imageModules).map((key) => imageModules[key].name);	
  const imagePath = Object.keys(imageModules).map((key) => imageModules[key].name.split('/').pop());	

  export let interval = 3500;
</script>
  

<div class="justify-center items-center ">
  <h1 class="my-10 text-4xl text-center">WeLaser</h1>

  <h2 class="my-10 text-2xl text-center">IoT Dashboard</h2>
</div>

<Galery {interval} imagePath={imagePath} />