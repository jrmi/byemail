<template>
  <div id="app" class="container">
    <md-toolbar id="topbar">
      <h1 class="md-title">Leefmail</h1>
    </md-toolbar>
    <router-view></router-view>
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
  height: 100vh;
  display: flex;
  flex-direction: column;
}
#topbar{
  flex: 0;
}
</style>
