<script lang="ts">
  import { base } from "$app/paths"    
  const imageModules = import.meta.glob("$lib/assets/*.jpg"); 
  const imagePath = Object.keys(imageModules).map((key) => imageModules[key].name);	
</script>

<!-- <pre>{JSON.stringify(imagePath)}</pre> -->
<div class="grid grid-cols-2 gap-4 m-4">
	{#each imagePath as src }
    <div class="col-span-2 md:col-span-1">
        <img src={src} class="w-full h-auto" alt="{src}"/>
        <p class="text-center">{src.split('/').pop().replace(/\.[^/.]+$/, '')}</p>
    </div>
    {/each}

</div>