<script lang='ts'>
  export let name: string
  export let value: any

  BigInt.prototype.toJSON = function () {
    return this.toString();
  };

</script>

<section>
  <h1>{name}</h1>
  <pre>{JSON.stringify(value, null, 2)}</pre>
</section>