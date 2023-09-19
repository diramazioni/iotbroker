	<script>
		import ThemeSwitch from '$lib/ThemeSwitch.svelte';
		
		import { afterNavigate } from '$app/navigation';
		import { page } from '$app/stores'
		import { base } from '$app/paths'
		
		import { menu } from '$lib/constant'
		// Carbon charts
		import '../app.postcss';
		import "carbon-components-svelte/css/all.css";
		// import "carbon-components-svelte/css/white.css";
		// import "carbon-components-svelte/css/g90.css";

	// Scroll to top
	afterNavigate((params) => {
	});



	
</script>


<div class="grid items-center grid-flow-col auto-cols-auto gap-4 space-y-4 p-4">
	<div class="flex justify-between items-center place-self-start max-w-0">
		<div class="flex-none">
			<h3 class="h3">WeLaser</h3>
			<h4 class="h4">iot dashboard</h4>
		</div>
	</div> 
	<nav class="flex-auto place-self-center">
		{#each menu as {name, href}}
		<a
		href={href}					
		class="button"
		aria-current={$page.url.pathname === href ? 'page' : null}>
			{name}
		</a>					
		{/each}
	</nav>
	<div class="flex-none flex "> 
		<ThemeSwitch />
	</div>
</div> 

<slot />
<style lang="postcss">


	/* :global(div.legend-item.active p){
		color: red;
	} */
</style>