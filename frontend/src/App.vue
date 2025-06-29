레이아웃 문제를 해결하기 위해 컴포넌트들을 다시 활성화하고 적절한 구조로 수정하겠습니다.
<script setup lang="ts">
import HeaderBar from './layout/HeaderBar.vue'
import MainContent from './layout/MainContent.vue'
import FooterBar from './layout/FooterBar.vue'
</script>

<template>
  <div class="app dark-theme">
    <HeaderBar />
    <MainContent />
    <FooterBar />
  </div>
</template>

<style scoped>
.app.dark-theme {
  min-height: 100vh;
  background: linear-gradient(135deg, #181c24 0%, #23283a 100%);
  color: #f3f4f6;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
