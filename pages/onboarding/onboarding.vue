<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-left"></view>
    <view class="ambient ambient-right"></view>

    <view class="header">
      <text class="brand">AuraPose</text>
      <text class="header-tag">{{ copy.headerTag }}</text>
    </view>

    <view class="hero">
      <text class="hero-kicker">{{ copy.heroKicker }}</text>
      <text class="hero-title">{{ copy.heroTitle }}</text>
    </view>

    <view class="panel">
      <view class="identity-block">
        <view class="avatar-shell" @click="pickAvatar">
          <image v-if="avatarPath" class="avatar-image" :src="avatarPath" mode="aspectFill" />
          <view v-else class="avatar-placeholder">
            <text class="avatar-plus">+</text>
            <text class="avatar-tip">{{ copy.avatarTip }}</text>
          </view>
        </view>
        <input
          v-model="nickname"
          class="nickname-input"
          maxlength="20"
          :placeholder-style="placeholderStyle"
          :placeholder="copy.nicknamePlaceholder"
        />
      </view>

      <view class="compact-grid">
        <view class="metric-card metric-card-wide">
          <view class="metric-head">
            <text class="metric-label">{{ copy.ageLabel }}</text>
            <text class="metric-value">{{ age }} {{ copy.ageUnit }}</text>
          </view>
          <slider
            class="age-slider"
            :value="age"
            :min="16"
            :max="60"
            :block-size="20"
            :activeColor="themeMode === 'light' ? '#4c6fff' : '#9cb3ff'"
            :backgroundColor="themeMode === 'light' ? '#d7dfee' : '#24304f'"
            @change="handleAgeChange"
          />
          <view class="age-range">
            <text>16 {{ copy.ageUnit }}</text>
            <text>60 {{ copy.ageUnit }}</text>
          </view>
        </view>

        <view class="metric-card">
          <text class="metric-label">{{ copy.heightLabel }}</text>
          <view class="metric-input-row">
            <input
              v-model="height"
              class="metric-input"
              type="number"
              :placeholder-style="placeholderStyle"
              placeholder="180"
            />
            <text class="metric-unit">cm</text>
          </view>
        </view>

        <view class="metric-card">
          <text class="metric-label">{{ copy.weightLabel }}</text>
          <view class="metric-input-row">
            <input
              v-model="weight"
              class="metric-input"
              type="number"
              :placeholder-style="placeholderStyle"
              placeholder="75"
            />
            <text class="metric-unit">kg</text>
          </view>
        </view>
      </view>

      <view class="privacy-row">
        <text class="privacy-text">{{ copy.privacyText }}</text>
        <text class="privacy-chip">{{ themeMode === 'light' ? copy.dayMode : copy.nightMode }}</text>
      </view>
    </view>

    <button class="submit-btn" @click="generatePlan">{{ copy.submitButton }}</button>
  </view>
</template>

<script>
import {
  applyNativeTheme,
  getStoredProfile,
  getThemeClass,
  getThemeMode,
  getThemeVars,
  mergeStoredProfile
} from '../../common/theme.js'
import { applyPageLocale, getCopy, getLocale } from '../../common/i18n.js'

export default {
  data() {
    const profile = getStoredProfile()
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      nickname: profile.nickname || '',
      age: Number(profile.age || 28),
      height: String(profile.height || 180),
      weight: String(profile.weight || 75),
      avatarPath: profile.avatarPath || ''
    }
  },
  computed: {
    copy() {
      return getCopy('onboarding', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    placeholderStyle() {
      return `color:${this.themeMode === 'light' ? '#9aa5b5' : '#66738f'}`
    }
  },
  onLoad() {
    this.syncLocale()
  },
  onShow() {
    this.syncTheme()
    this.syncLocale()
    const profile = getStoredProfile()
    this.avatarPath = profile.avatarPath || this.avatarPath
  },
  methods: {
    syncTheme() {
      this.themeMode = getThemeMode()
      applyNativeTheme(this.themeMode)
    },
    syncLocale() {
      this.locale = getLocale()
      applyPageLocale('onboarding', this.locale)
    },
    handleAgeChange(event) {
      this.age = Number(event.detail.value || 28)
    },
    pickAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: (res) => {
          const tempPath = res.tempFilePaths[0] || ''
          if (!tempPath) {
            return
          }
          uni.navigateTo({
            url: `/pages/avatar-crop/avatar-crop?src=${encodeURIComponent(tempPath)}`
          })
        }
      })
    },
    async generatePlan() {
      const payload = {
        nickname: (this.nickname || '').trim() || this.copy.defaultNickname,
        age: Number(this.age || 28),
        height: Number(this.height || 0),
        weight: Number(this.weight || 0),
        avatarPath: this.avatarPath
      }

      mergeStoredProfile(payload)
      uni.switchTab({ url: '/pages/home/home' })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 40rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top left, var(--hero-glow), transparent 36%),
    radial-gradient(circle at right center, var(--hero-glow-alt), transparent 26%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(54rpx);
  opacity: 0.8;
}

.ambient-left {
  width: 240rpx;
  height: 240rpx;
  background: var(--hero-glow);
  left: -80rpx;
  top: 240rpx;
}

.ambient-right {
  width: 280rpx;
  height: 280rpx;
  background: var(--hero-glow-alt);
  right: -120rpx;
  top: 140rpx;
}

.header,
.hero,
.panel,
.submit-btn {
  position: relative;
  z-index: 2;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 44rpx;
}

.brand {
  font-size: 48rpx;
  font-weight: 700;
  letter-spacing: -1rpx;
  color: var(--brand);
}

.header-tag {
  padding: 14rpx 24rpx;
  border-radius: 999rpx;
  background: var(--surface);
  color: var(--text-secondary);
  font-size: 22rpx;
  border: 1rpx solid var(--border);
}

.hero {
  margin-bottom: 36rpx;
}

.hero-kicker {
  display: block;
  margin-bottom: 16rpx;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.hero-title {
  display: block;
  font-size: 64rpx;
  line-height: 1.08;
  font-weight: 700;
  margin-bottom: 16rpx;
}

.panel {
  padding: 32rpx;
  border-radius: 36rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(24rpx);
}

.identity-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 28rpx;
}

.avatar-shell {
  width: 176rpx;
  height: 176rpx;
  padding: 6rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  box-shadow: 0 18rpx 40rpx rgba(76, 111, 255, 0.2);
  margin-bottom: 20rpx;
}

.avatar-image,
.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-placeholder {
  background: var(--surface-strong);
  border: 1rpx dashed var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-plus {
  font-size: 58rpx;
  line-height: 1;
  color: var(--brand);
}

.avatar-tip {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
}

.nickname-input {
  width: 100%;
  height: 90rpx;
  padding: 0 28rpx;
  border-radius: 24rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
  color: var(--text);
  font-size: 30rpx;
  text-align: center;
  box-sizing: border-box;
}

.compact-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.metric-card {
  padding: 24rpx;
  border-radius: 28rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
}

.metric-card-wide {
  grid-column: 1 / -1;
}

.metric-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  display: block;
  font-size: 22rpx;
  letter-spacing: 3rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.metric-value {
  font-size: 42rpx;
  font-weight: 700;
  color: var(--brand);
}

.age-slider {
  margin: 8rpx 0 0;
}

.age-range {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 22rpx;
}

.metric-input-row {
  display: flex;
  align-items: flex-end;
  gap: 10rpx;
  margin-top: 24rpx;
}

.metric-input {
  flex: 1;
  min-width: 0;
  font-size: 50rpx;
  font-weight: 700;
  color: var(--text);
}

.metric-unit {
  font-size: 24rpx;
  color: var(--text-secondary);
  padding-bottom: 10rpx;
}

.privacy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
  margin-top: 24rpx;
}

.privacy-text {
  flex: 1;
  font-size: 22rpx;
  line-height: 1.6;
  color: var(--text-secondary);
}

.privacy-chip {
  flex-shrink: 0;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: var(--surface-tint);
  color: var(--brand);
  font-size: 22rpx;
}

.submit-btn {
  margin-top: 28rpx;
  height: 96rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, var(--brand), var(--brand-soft));
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 34rpx;
  line-height: 1;
  font-weight: 700;
  box-shadow: var(--shadow);
}

.submit-btn::after {
  border: none;
}
</style>
