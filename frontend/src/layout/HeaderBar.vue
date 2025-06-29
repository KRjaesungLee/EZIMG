<template>
  <header class="header-bar">
    <div class="header-inner">
      <div class="logo-section">
        <img src="@/assets/icons/ezimg-logo.svg" alt="EZIMG 로고" class="logo-icon" />
      </div>
      <nav class="nav-menu">
        <button class="nav-item">
          <img src="@/assets/icons/photo.svg" alt="이미지" class="nav-icon" />
          <span>{{ $t('image') }}</span>
        </button>
        <button class="nav-item">
          <img src="@/assets/icons/video.svg" alt="동영상" class="nav-icon" />
          <span>{{ $t('video') }}</span>
        </button>
        <button class="nav-item login-btn">
          <img src="@/assets/icons/user.svg" alt="로그인" class="nav-icon" />
          <span>{{ $t('login') }}</span>
        </button>
        <div class="lang-switch">
          <button :class="['lang-btn', { active: locale === 'ko' }]" @click="setLang('ko')">🇰🇷</button>
          <button :class="['lang-btn', { active: locale === 'en' }]" @click="setLang('en')">🇺🇸</button>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()
const setLang = (lang: string) => {
  locale.value = lang
}
</script>

<style scoped>
.header-bar {
  width: 100%;
  background: #181c24;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 72px;
}
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-icon {
  width: 2rem;
  height: 2rem;
  display: block;
  filter: drop-shadow(0 2px 8px rgba(102,126,234,0.15));
}
.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #b3b3b3;
  font-size: 1rem;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.nav-item:hover {
  background: #23283a;
  color: #fff;
}
.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  display: block;
  filter: drop-shadow(0 1px 4px rgba(102,126,234,0.10));
  color: #fff;
}
.login-btn {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
  margin-left: 12px;
  box-shadow: 0 2px 8px rgba(102,126,234,0.15);
}
.login-btn:hover {
  background: linear-gradient(90deg, #5a67d8 0%, #6b46c1 100%);
}
.lang-switch {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: 10px;
}
.lang-btn {
  background: none;
  border: none;
  font-size: 1.15rem;
  padding: 4px 8px;
  border-radius: 6px;
  color: #b3b3b3;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.lang-btn.active, .lang-btn:hover {
  background: #23283a;
  color: #fff;
  font-weight: bold;
}
@media (max-width: 768px) {
  .header-inner {
    padding: 0 12px;
    height: 56px;
  }
  .nav-item {
    font-size: 0.95rem;
    padding: 6px 10px;
  }
  .logo-icon {
    width: 1.3rem;
    height: 1.3rem;
  }
  .nav-icon {
    width: 1rem;
    height: 1rem;
  }
  .lang-btn {
    font-size: 1rem;
    padding: 2px 5px;
  }
}
</style> 