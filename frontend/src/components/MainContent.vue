<template>
  <main class="main-content">
    <DalleImageGenerator />
  </main>
</template>

<script setup lang="ts">
import DalleImageGenerator from './DalleImageGenerator.vue'
</script>

<style scoped>
.main-content {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}
</style> 