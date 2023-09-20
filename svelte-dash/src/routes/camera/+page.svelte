<script lang="ts"> 
  // const imageModules = import.meta.glob("$lib/assets/*.jpg"); 
  // const imagePath = Object.keys(imageModules).map((key) => imageModules[key].name.split('/').pop());	
  let field_images:string[] = []
  let robot_images:string[] = []
  const baseUrl =  process.env.NODE_ENV === 'production' ? "/data/" : "/" // https://greenlab.unibo.it/data
  const imageUrl = baseUrl + "images.json"

  $: fetch(imageUrl)
	.then(response => response.json())
  .then(data => {
    field_images = data.field;
    robot_images = data.robot;
  })
  $: console.log(field_images)
</script>

<!-- <pre>{JSON.stringify(imagePath)}</pre> -->
<h1>field images</h1>
<div class="grid grid-cols-2 gap-4 m-4">
	{#each field_images as src }
    <div class="col-span-2 md:col-span-1">
        <img src={baseUrl + src} class="w-full h-auto" alt="{src}"/>
        <p class="text-center">{src.replace(/\.[^/.]+$/, '')}</p>
    </div>
  {/each}

</div>
<h1>Robot images</h1>
<div class="grid grid-cols-2 gap-4 m-4">
	{#each robot_images as src }
    <div class="col-span-2 md:col-span-1">
        <img src={baseUrl + src} class="w-full h-auto" alt="{src}"/>
        <p class="text-center">{src.replace(/\.[^/.]+$/, '')}</p>
    </div>
    {/each}

</div>