<script lang="ts">
	import { T } from '@threlte/core'
	import { BufferGeometry, Float32BufferAttribute } from 'three'

	export let points2d 
	export let points3d 
	export let vertices
	export let color

	const dataLength = points3d.length;

/*
	for (var i = 0, l = dataLength, p; i < l; i++) {
                p = points3d[i];

                vertices[i].x = vertices[i + l].x = p[0].x;
                vertices[i].y = vertices[i + l].y = p[1].y;

                vertices[i].z = p[2].z;
                vertices[i + l].z = p[2].z + depth;
            }	*/



</script>

<T.Mesh>
	<T.PlaneGeometry 
		args={[10, 10, dataLength, dataLength]} 
		on:create={({ ref }) => {
			ref.setAttribute('position', new Float32BufferAttribute(vertices, 3))
			//ref.computeFaceNormals();		
		}} />

<!--
    <T.PlaneGeometry 
        args={[10, 10, dataLength, 10]} 
        on:create={({ ref }) => {
            let depth = 3
			let vert = ref.getAttribute('position').array;
            for (var i = 0, l = dataLength; i < l; i++) {
                let p = points3d[i];

                vert[i].x = vert[i + l].x = p.x;
                vert[i].y = vert[i + l].y = p.y;

                vert[i].z = p.z;
                vert[i + l].z = p.z + depth;
            }

                
            //ref.computeFaceNormals();        
        }} />			
-->
		<T.MeshBasicMaterial wireframe={true} {color} /> 
	<!-- <T.MeshLambertMaterial {color} side={T.DoubleSide}/> -->
	<!-- <T.MeshNormalMaterial side={T.DoubleSide} /> -->
</T.Mesh>

