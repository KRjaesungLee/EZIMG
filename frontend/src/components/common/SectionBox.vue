<!-- 재사용 가능한 섹션 박스 컴포넌트 -->
<template>
  <div 
    class="section-box"
    :class="{
      'with-header': withHeader,
      'with-shadow': withShadow,
      'with-border': withBorder,
      [variant]: true
    }"
  >
    <div v-if="withHeader" class="section-header">
      <slot name="header"></slot>
    </div>
    <div class="section-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  withHeader?: boolean;
  withShadow?: boolean;
  withBorder?: boolean;
  variant?: 'default' | 'dark' | 'light';
}

withDefaults(defineProps<Props>(), {
  withHeader: false,
  withShadow: true,
  withBorder: true,
  variant: 'default'
});
</script>

<style scoped>
.section-box {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
}

.section-box.with-shadow {
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05),
              0 1px 15px rgba(0, 0, 0, 0.1);
}

.section-box.with-border {
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.section-header {
  text-align: center;
  padding-bottom: 10px;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.section-content {
  position: relative;
}

/* 변형 스타일 */
.section-box.default {
  background: rgba(255, 255, 255, 0.03);
  padding: 24px;
}

.section-box.dark {
  background: rgba(0, 0, 0, 0.2);
  padding: 24px;
}

.section-box.light {
  background: rgba(255, 255, 255, 0.08);
  padding: 24px;
}

/* 반응형 */
@media (max-width: 768px) {
  .section-box {
    padding: 16px;
  }
}
</style> 