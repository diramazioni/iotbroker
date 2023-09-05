<script lang="ts">
  import { base } from "$app/paths";
	import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import { setContext } from 'svelte';
  import type { LayoutData } from './$types'
  import { page } from '$app/stores';

  import "carbon-components-svelte/css/white.css";
  import '../app.css'

   import Pre from '$lib/pre.svelte'

  export let data: LayoutData

</script>

<nav class="w-full flex p-3 gap-2 justify-center items-center">
	<a class="hover:bg-blue-500 hover:text-white " href="{base}/" aria-current={$page.url.pathname === "/{base}/"}>Home</a>
	<a class="hover:bg-blue-500 hover:text-white " href="{base}/d/weatherstation_n" aria-current={$page.url.pathname === "/{base}/weatherstation_n"}>Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/d/weatherstation_v" aria-current={$page.url.pathname === "/{base}/weatherstation_v"}>Virtual Weather Stations</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/d/etrometer" aria-current={$page.url.pathname === "/{base}/etrometer"}>Etrometers</a>
  <a class="hover:bg-blue-500 hover:text-white " href="{base}/camera" aria-current={$page.url.pathname === "/{base}/camera"}>Cameras</a>
</nav>

<slot />
<!-- 
<Pre name="export let data" value={data} />
<Pre name="page data" value={$page.data} /> -->
<!-- <Pre name="incoming" value={incoming.length} /> -->



<style>
  			/* nav {
				position: relative;
				display: flex;
				gap: 1em;
				padding: 1em;
				background: var(--bg-2);
				z-index: 2;
				margin: 0 0 1em 0;
				border-radius: var(--border-radius);
			} */
			nav a {
				text-decoration: none;
			}

			nav a[aria-current='true'] {
				border-bottom: 2px solid;
			}      
</style>