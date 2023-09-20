<script>
	import { T } from '@threlte/core'
  import * as Three from 'three'
  export let size = 20
  export let division = 20
	export let x = 0
	export let z = 0
  // const gridHelper = new Three.GridHelper
  // const axesHelper = new Three.AxesHelper(5)
</script>

<T.GridHelper 
  args={[size, division, "#ff000f", "#ffccaa"]}  	
  position.x={x}
  position.y={0.01}
  position.z={z}/>



