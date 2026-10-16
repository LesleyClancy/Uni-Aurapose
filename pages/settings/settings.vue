<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-left"></view>
    <view class="ambient ambient-right"></view>

    <view class="hero">
      <text class="hero-kicker">{{ copy.heroKicker }}</text>
      <text class="hero-title">{{ copy.heroTitle }}</text>
      <text class="hero-subtitle">{{ copy.heroSubtitle }}</text>
    </view>

    <view class="setting-card">
      <text class="card-title">{{ copy.themeTitle }}</text>
      <view class="option-grid">
        <button
          v-for="item in themeOptions"
          :key="item.value"
          :class="['option-btn', { active: themeMode === item.value }]"
          @click="handleThemeChange(item.value)"
        >
          {{ item.label }}
        </button>
      </view>
    </view>

    <view class="setting-card">
      <text class="card-title">{{ copy.languageTitle }}</text>
      <view class="option-grid">
        <button
          v-for="item in languageOptions"
          :key="item.value"
          :class="['option-btn', { active: locale === item.value }]"
          @click="handleLanguageChange(item.value)"
        >
          {{ item.label }}
        </button>
      </view>
    </view>

    <!-- #ifdef APP-PLUS -->
    <view class="setting-card">
      <text class="card-title">{{ copy.serverTitle }}</text>
      <input
        class="server-input"
        v-model="serverUrl"
        :placeholder="defaultApiBaseUrl"
        placeholder-class="server-placeholder"
      />
      <text class="server-hint">{{ copy.serverHint }}</text>
      <button class="option-btn server-save" @click="handleServerSave">{{ copy.serverSave }}</button>
    </view>
    <!-- #endif -->
  </view>
</template>

<script>
import {
  applyNativeTheme,
  getThemeClass,
  getThemeMode,
  getThemeVars,
  setThemeMode
} from '../../common/theme.js'
import {
  applyPageLocale,
  getCopy,
  getLocale,
  setLocale
} from '../../common/i18n.js'
import { DEFAULT_API_BASE_URL, getApiBaseUrl, setApiBaseUrl } from '../../common/api.js'

export default {
  data() {
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      serverUrl: getApiBaseUrl(),
      defaultApiBaseUrl: DEFAULT_API_BASE_URL
    }
  },
  computed: {
    copy() {
      return getCopy('settings', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    themeOptions() {
      return [
        { label: this.copy.themeLight, value: 'light' },
        { label: this.copy.themeDark, value: 'dark' }
      ]
    },
    languageOptions() {
      return [
        { label: this.copy.languageZh, value: 'zh' },
        { label: this.copy.languageEn, value: 'en' }
      ]
    }
  },
  onLoad() {
    this.syncTheme()
    this.syncLocale()
  },
  onShow() {
    this.syncTheme()
    this.syncLocale()
  },
  methods: {
    syncTheme() {
      this.themeMode = getThemeMode()
      applyNativeTheme(this.themeMode)
    },
    syncLocale() {
      this.locale = getLocale()
      applyPageLocale('settings', this.locale)
    },
    handleThemeChange(mode) {
      this.themeMode = setThemeMode(mode)
      applyNativeTheme(this.themeMode)
    },
    handleLanguageChange(locale) {
      this.locale = setLocale(locale)
      applyPageLocale('settings', this.locale)
    },
    handleServerSave() {
      this.serverUrl = setApiBaseUrl(this.serverUrl)
      uni.showToast({
        title: this.copy.serverSaved,
        icon: 'none'
      })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 36rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top right, var(--hero-glow), transparent 34%),
    radial-gradient(circle at left bottom, var(--hero-glow-alt), transparent 26%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(80rpx);
}

.ambient-left {
  width: 260rpx;
  height: 260rpx;
  left: -90rpx;
  top: 220rpx;
  background: var(--hero-glow-alt);
}

.ambient-right {
  width: 280rpx;
  height: 280rpx;
  right: -110rpx;
  top: 120rpx;
  background: var(--hero-glow);
}

.hero,
.setting-card {
  position: relative;
  z-index: 2;
}

.hero {
  margin-bottom: 28rpx;
}

.hero-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.hero-title {
  display: block;
  margin-top: 14rpx;
  font-size: 60rpx;
  line-height: 1.08;
  font-weight: 700;
}

.hero-subtitle {
  display: block;
  margin-top: 16rpx;
  font-size: 26rpx;
  line-height: 1.6;
  color: var(--text-secondary);
}

.setting-card {
  margin-bottom: 20rpx;
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18rpx);
}

.card-title {
  display: block;
  margin-bottom: 22rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: var(--text-secondary);
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.option-btn {
  height: 104rpx;
  border-radius: 28rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
  color: var(--text-secondary);
  font-size: 32rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.option-btn.active {
  background: linear-gradient(135deg, var(--brand), var(--brand-soft));
  color: #ffffff;
  box-shadow: 0 18rpx 36rpx rgba(76, 111, 255, 0.24);
}

.option-btn::after {
  border: none;
}

.server-input {
  width: 100%;
  box-sizing: border-box;
  height: 88rpx;
  padding: 0 24rpx;
  border-radius: 24rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
  color: var(--text);
  font-size: 28rpx;
}

.server-placeholder {
  color: var(--text-muted);
}

.server-hint {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  color: var(--text-muted);
}

.server-save {
  margin-top: 18rpx;
  width: 100%;
}
</style>
