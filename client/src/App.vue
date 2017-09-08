<template>
  <div id="app" class="container">
    <md-toolbar>
      <h1 class="md-title">Leefmail</h1>
    </md-toolbar>
    <router-view class="main-content"></router-view>
  </div>
</template>

<script>
export default {
  name: 'app'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}
</style>
