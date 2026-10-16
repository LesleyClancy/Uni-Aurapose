<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-a"></view>
    <view class="ambient ambient-b"></view>

    <view class="header">
      <text class="brand">AuraPose</text>
    </view>

    <view class="hero-card" @click="navigateToStrength">
      <image class="hero-image" :src="featuredHero.image" mode="aspectFill" />
      <view class="hero-mask"></view>
      <view class="hero-content">
        <text class="hero-kicker">{{ featuredHero.tag }}</text>
        <text class="hero-title">{{ featuredHero.title }}</text>
        <view class="hero-meta">
          <text>{{ featuredHero.duration }}</text>
          <text>{{ featuredHero.level }}</text>
        </view>
      </view>
    </view>

    <view class="section-head">
      <view>
        <text class="section-kicker">{{ copy.sectionKicker }}</text>
        <text class="section-title">{{ copy.sectionTitle }}</text>
      </view>
    </view>

    <view class="category-grid">
      <view class="category-card" v-for="item in categories" :key="item.name" @click="item.action && item.action()">
        <image class="category-icon-image" :src="item.icon" mode="aspectFit" />
        <text class="category-name">{{ item.name }}</text>
      </view>
    </view>

    <view class="section-head section-head-gap">
      <view>
        <text class="section-kicker">{{ copy.smartKicker }}</text>
        <text class="section-title">{{ copy.smartTitle }}</text>
      </view>
      <text class="section-link">{{ copy.smartLink }}</text>
    </view>

    <view class="editorial-list">
      <view class="editorial-card" v-for="item in editorialCards" :key="item.title" @click="item.action && item.action()">
        <image class="editorial-image" :src="item.image" mode="aspectFill" />
        <view class="editorial-body">
          <view class="editorial-top">
            <text class="editorial-tag">{{ item.tag }}</text>
            <text class="editorial-time">{{ item.duration }}</text>
          </view>
          <text class="editorial-title">{{ item.title }}</text>
          <text class="editorial-copy">{{ item.description }}</text>
        </view>
      </view>
    </view>

    <view class="spotlight-card">
      <view class="spotlight-copy">
        <text class="section-kicker">{{ copy.spotlightKicker }}</text>
        <text class="spotlight-title">{{ copy.spotlightTitle }}</text>
        <text class="spotlight-text">{{ copy.spotlightText }}</text>
      </view>
      <view class="spotlight-metrics">
        <view class="spotlight-metric" v-for="item in spotlightMetrics" :key="item.label">
          <text class="spotlight-label">{{ item.label }}</text>
          <text class="spotlight-value">{{ item.value }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { fetchBootstrap } from '../../common/api.js'
import {
  applyNativeTheme,
  getSceneAsset,
  getThemeClass,
  getThemeMode,
  getThemeVars
} from '../../common/theme.js'
import { applyPageLocale, getCopy, getLocale } from '../../common/i18n.js'

export default {
  data() {
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      bootstrap: null
    }
  },
  computed: {
    copy() {
      return getCopy('fitness', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    spotlightMetrics() {
      return [
        { label: this.copy.spotlightIntensity, value: '15 min' },
        { label: this.copy.spotlightRecovery, value: '20 min' },
        { label: this.copy.spotlightWeekly, value: this.locale === 'zh' ? '每周 4 次' : '4 sessions' }
      ]
    },
    featuredHero() {
      return {
        tag: this.copy.featuredTag,
        title: this.copy.featuredTitle,
        duration: this.copy.featuredDuration,
        level: this.copy.featuredLevel,
        image: getSceneAsset('hiitBurn', this.themeMode)
      }
    },
    categories() {
      return [
        {
          name: this.copy.categoryStrength,
          icon: '/static/icons/category-strength.png',
          action: this.navigateToStrength
        },
        {
          name: this.copy.categoryCardio,
          icon: '/static/icons/category-cardio.png'
        },
        {
          name: this.copy.categoryRecovery,
          icon: '/static/icons/category-recovery.png'
        },
        {
          name: this.copy.categoryAi,
          icon: '/static/icons/category-ai.png'
        }
      ]
    },
    editorialCards() {
      return [
        {
          tag: this.copy.cardCoreTag,
          title: this.copy.cardCoreTitle,
          duration: this.copy.cardCoreDuration,
          description: this.copy.cardCoreDescription,
          image: getSceneAsset('coreBurst', this.themeMode),
          action: this.navigateToStrength
        },
        {
          tag: this.copy.cardStretchTag,
          title: this.copy.cardStretchTitle,
          duration: this.copy.cardStretchDuration,
          description: this.copy.cardStretchDescription,
          image: getSceneAsset('deepStretch', this.themeMode)
        },
        {
          tag: this.copy.cardYogaTag,
          title: this.copy.cardYogaTitle,
          duration: this.copy.cardYogaDuration,
          description: this.copy.cardYogaDescription,
          image: getSceneAsset('flowYoga', this.themeMode)
        }
      ]
    }
  },
  onLoad() {
    this.syncLocale()
    this.loadBootstrap()
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
      applyPageLocale('fitness', this.locale)
    },
    async loadBootstrap() {
      try {
        this.bootstrap = await fetchBootstrap()
      } catch (err) {
        console.warn('bootstrap failed', err)
      }
    },
    navigateToStrength() {
      uni.navigateTo({ url: '/pages/strength/strength' })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 36rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top left, var(--hero-glow), transparent 30%),
    radial-gradient(circle at 85% 40%, var(--hero-glow-alt), transparent 24%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(76rpx);
}

.ambient-a {
  width: 280rpx;
  height: 280rpx;
  right: -120rpx;
  top: 220rpx;
  background: var(--hero-glow);
}

.ambient-b {
  width: 240rpx;
  height: 240rpx;
  left: -100rpx;
  bottom: 200rpx;
  background: var(--hero-glow-alt);
}

.header,
.hero-card,
.section-head,
.category-grid,
.editorial-list,
.spotlight-card {
  position: relative;
  z-index: 2;
}

.header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 28rpx;
}

.brand {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  color: var(--brand);
}

.hero-card {
  position: relative;
  height: 520rpx;
  border-radius: 40rpx;
  overflow: hidden;
  box-shadow: var(--shadow);
  margin-bottom: 32rpx;
}

.hero-image,
.hero-mask {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.hero-mask {
  background: linear-gradient(180deg, rgba(8, 10, 18, 0.08) 0%, rgba(8, 10, 18, 0.78) 100%);
}

.hero-content {
  position: absolute;
  left: 28rpx;
  right: 28rpx;
  bottom: 28rpx;
  color: #ffffff;
}

.hero-kicker,
.section-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
}

.hero-title {
  display: block;
  margin-top: 14rpx;
  font-size: 58rpx;
  line-height: 1.08;
  font-weight: 700;
}

.hero-meta {
  margin-top: 18rpx;
  display: flex;
  gap: 18rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.section-head {
  margin-bottom: 18rpx;
}

.section-head-gap {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 8rpx;
}

.section-title {
  display: block;
  margin-top: 10rpx;
  font-size: 48rpx;
  font-weight: 700;
}

.section-link {
  font-size: 24rpx;
  color: var(--brand);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
  margin-bottom: 34rpx;
}

.category-card {
  padding: 24rpx;
  border-radius: 28rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.category-icon-image {
  width: 92rpx;
  height: 92rpx;
  border-radius: 26rpx;
  margin-bottom: 22rpx;
  display: block;
}

.category-name {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
}

.editorial-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  margin-bottom: 30rpx;
}

.editorial-card {
  display: flex;
  gap: 18rpx;
  padding: 18rpx;
  border-radius: 30rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.editorial-image {
  width: 224rpx;
  height: 224rpx;
  border-radius: 24rpx;
  flex-shrink: 0;
}

.editorial-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.editorial-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
}

.editorial-tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: var(--surface-tint);
  color: var(--brand);
  font-size: 20rpx;
}

.editorial-time {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.86);
}

.editorial-title {
  display: block;
  margin-top: 16rpx;
  font-size: 34rpx;
  line-height: 1.2;
  font-weight: 700;
}

.editorial-copy {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.65;
  color: var(--text-secondary);
}

.spotlight-card {
  padding: 30rpx;
  border-radius: 34rpx;
  background: linear-gradient(180deg, var(--surface) 0%, var(--surface-soft) 100%);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.spotlight-title {
  display: block;
  margin-top: 12rpx;
  font-size: 42rpx;
  line-height: 1.2;
  font-weight: 700;
}

.spotlight-text {
  display: block;
  margin-top: 14rpx;
  font-size: 25rpx;
  line-height: 1.68;
  color: var(--text-secondary);
}

.spotlight-metrics {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
}

.spotlight-metric {
  padding: 20rpx 16rpx;
  border-radius: 22rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
}

.spotlight-label,
.spotlight-value {
  display: block;
}

.spotlight-label {
  font-size: 20rpx;
  color: var(--text-muted);
}

.spotlight-value {
  margin-top: 10rpx;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
