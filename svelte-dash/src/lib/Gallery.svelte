<script>
	import { json } from '@sveltejs/kit';
	import {fade, blur, fly, scale, slide} from 'svelte/transition'
	import { quintOut,elasticOut, sineOut } from 'svelte/easing';
	
	//import { onInterval } from './utils.js';

	export let interval = 1000;
	export let imagePath = [
			'https://picsum.photos/800/400?random=1',
			'https://picsum.photos/800/400?random=2',
			'https://picsum.photos/800/400?random=3'
		];


	let index = 0
	
	const next = () => {
		index = (index + 1) % imagePath.length
	}
	const prev = () => {
		if (index !== 0) {
			index = (index - 1) % imagePath.length
		}
	}
	let clear
	$: {
		clearInterval(clear)
		clear = setInterval(next, interval)
	}


	function handleKeyDown(event) {
    if (event.key === "<") {
			console.log("next")
      next();
     }else if (event.key === ">") {
			console.log("prev")
      prev();
    }
  }
	/*	Show custom transitions */
	function fadeSlide(node, options) {
		const slideTrans = slide(node, options)
		return {
			duration: options.duration,
			css: t => `
				${slideTrans.css(t)}
				opacity: ${t};
			`
		};
	}
	function maximizeImageSize(img) {
    const container = document.querySelector('.img_abs');
    const containerAspectRatio = container.offsetWidth / container.offsetHeight;
    const imageAspectRatio = img.naturalWidth / img.naturalHeight;
    if (containerAspectRatio > imageAspectRatio) {
      // Container is wider, resize the image to fit the container's height
      img.style.width = 'auto';
      img.style.height = '100%';
    } else {
      // Container is taller, resize the image to fit the container's width
      img.style.width = '100%';
      img.style.height = 'auto';
    }
  }

	let running = true;
	function focusImg(e) {
		const img = e.target;
		const classes = e.target.parentElement.classList;
		if (running) {
			clearTimeout(clear);
			classes.add("img_abs")
			classes.remove("img_cont")
			maximizeImageSize(img)
		} else {
			classes.remove("img_abs")
			classes.add("img_cont")
			clear = setInterval(next, interval)
		}
		running = !running 
	}

</script>

<style>
  .img_cont {
    overflow: hidden;
		display: grid;
		justify-content: center;
  	align-items: center;
  }	
	:global(.img_abs) {
		position: absolute;
		top: 0;
		left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
		background-color: rgba(0, 0, 0, 0.8);
		z-index: 1000;
	}
	:global(.img_abs > img) {
    max-width: 100%;
    max-height: 100%;
	}
	.img_cont > img {
		justify-content: center;
  	align-items: center;
		/* text-align: center; */
		max-width: 800px;
    max-height: 400px;
		grid-column: 1/2;
		grid-row: 1/2		
	}

</style>
<!-- on:mouseenter={() => handleHover(true)} on:mouseleave={() => handleHover(false)} -->
<!-- <pre>{JSON.stringify(imagePath)}</pre> -->
<div class="img_cont" on:keydown={handleKeyDown}>
	{#each [imagePath[index]] as src (index)}
	<img transition:fadeSlide="{{duration: 200, easing: sineOut}}" {src} alt="" on:click={focusImg} tabIndex="0"/>	
	<!-- slide={{duration: 100, easing: sineOut}} -->
	{/each}
</div>
<!-- <button on:click={prev}>Prev!</button>
<button on:click={next}>Next!</button> -->
