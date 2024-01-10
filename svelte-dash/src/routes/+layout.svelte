<script>
	import ThemeSwitch from '$lib/ThemeSwitch.svelte';
	import { derived, writable } from 'svelte/store'
	import { afterNavigate } from '$app/navigation';
	import { page } from '$app/stores'
	import { base } from '$app/paths'

	import { menu } from '$lib/constant'
	// Carbon charts
	import '../app.postcss';
	import "carbon-components-svelte/css/all.css";
	// import "carbon-components-svelte/css/white.css";
	// import "carbon-components-svelte/css/g90.css";

	// svelte-toast
	import { SvelteToast } from '@zerodevx/svelte-toast'
	import { onMount } from 'svelte'
	import { browser } from '$app/environment'

	const options = 
		{ 
			// reversed: true, 
			// intro: { 
			// 	y: 192 
			// },
			pausable: true,
			duration: 10000,
			// Effectively disables autoclose when `initial`==`next`
  			//initial: 0,
		}
	

	// Scroll to top
	afterNavigate((params) => {
	});

	let showMenu = false;

	function toggleNavbar() {
		showMenu = !showMenu;
	}


</script>


<SvelteToast {options} />
<h3 class="h3 ml-3 hidden md:block">Iotbroker</h3>
<!-- container -->
<nav class=" py-6 mx-auto md:flex md:justify-between md:justify-center">
	<div class="flex md:hidden">
		<!-- Mobile menu button -->
		<button  type="button" on:click={toggleNavbar}
		class="flex md:hidden ml-4 text-blue-400 hover:text-blue-800 focus:outline-none focus:text-gray-400">
			<svg xmlns="http://www.w3.org/2000/svg"	fill="none"	viewBox="0 0 24 24"	stroke-width="1.5"	stroke="currentColor" class="w-6 h-6" >
				<path stroke-linecap="round"  stroke-linejoin="round"  d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
			</svg>
		</button>
		<!-- Mobile logo -->
		<h3 class="md:hidden h3 ml-3 h-3 -my-2">Iotbroker</h3>
	</div>
	<!-- Menu Links -->
	<div class="flex-col mt-4 space-y-4 md:ml-4 md:flex md:space-y-0 md:flex-row md:items-center  md:mt-0 
		{ showMenu ? 'flex' : 'hidden'}" >	
			{#each menu as {name, href}}
				<a href={href} 	class="button items-center"	aria-current={$page.url.pathname === href ? 'page' : null}
				on:click={toggleNavbar}>
					{name}
				</a>
			{/each}
	</div>

</nav>


<slot />
<style lang="postcss">


	/* :global(div.legend-item.active p){
		color: red;
	} */
</style>