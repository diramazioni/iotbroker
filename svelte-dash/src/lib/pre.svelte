<script lang='ts'>
  export let name: string
  export let value: any

</script>

<section>
  <h1>{name}</h1>
  <pre>{JSON.stringify(value, null, 2)}</pre>
</section>