<script setup>
  import { RouterLink, RouterView } from 'vue-router'
  import Navbar from './components/Navbar.vue'
  import Footer from './components/Footer.vue'
</script>

<template>
  <div id="app">
    <Navbar /> 
    <main>
      <RouterView />
    </main>
    <Footer />
  </div>
</template>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    background: #121212;
    color: #e2e2e8;
  }

  #app {
    width: 100%;
    min-height: 100vh;
  }

  main {
    min-height: calc(100vh - 80px);
  }
</style>