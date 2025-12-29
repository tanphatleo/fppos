<template>
  <!-- <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link>
  </nav> -->
  <!-- <nav>
    <router-link to="/">Home</router-link> |
  </nav> -->
  <router-view/>
</template>

<style lang="scss">
@import '../node_modules/bulma/';

:root {
  --bulma-body-overflow-y: hidden !important;
}

$kv-primary: #0070F4;
$size-sm: 4vh;
$main-bg-color: azure;

#app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  // overflow: hidden;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: $main-bg-color;
  overflow: hidden;
  // height: 100%;
}


</style>
