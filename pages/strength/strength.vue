<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-top"></view>
    <view class="ambient ambient-side"></view>

    <view class="module-list">
      <view class="module-card" v-for="item in modules" :key="item.title">
        <image class="module-image" :src="item.image" mode="aspectFill" />
        <view class="module-mask"></view>
        <view class="module-info">
          <view class="module-top">
            <text class="module-tag">{{ item.tag }}</text>
          </view>
          <text class="module-title">{{ item.title }}</text>
          <text class="module-copy">{{ copy.targetPrefix }}{{ item.target }}</text>
          <text class="module-copy">{{ item.tip }}</text>
          <button class="module-btn" @click="startTraining">{{ copy.startWorkout }}</button>
        </view>
      </view>
    </view>

    <view class="insight-card">
      <text class="section-kicker">{{ copy.suggestionKicker }}</text>
      <text class="insight-title">{{ copy.suggestionTitle }}</text>
      <text class="insight-text">{{ copy.suggestionText }}</text>
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
      return getCopy('strength', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    modules() {
      return [
        {
          tag: this.copy.moduleBicepsTag,
          title: this.copy.moduleBicepsTitle,
          target: this.copy.moduleBicepsTarget,
          tip: this.copy.moduleBicepsTip,
          image: getSceneAsset('bicepsCurl', this.themeMode)
        },
        {
          tag: this.copy.moduleCoreTag,
          title: this.copy.moduleCoreTitle,
          target: this.copy.moduleCoreTarget,
          tip: this.copy.moduleCoreTip,
          image: getSceneAsset('coreBurst', this.themeMode)
        },
        {
          tag: this.copy.modulePullTag,
          title: this.copy.modulePullTitle,
          target: this.copy.modulePullTarget,
          tip: this.copy.modulePullTip,
          image: getSceneAsset('pullUp', this.themeMode)
        },
        {
          tag: this.copy.moduleSquatTag,
          title: this.copy.moduleSquatTitle,
          target: this.copy.moduleSquatTarget,
          tip: this.copy.moduleSquatTip,
          image: getSceneAsset('squat', this.themeMode)
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
      applyPageLocale('strength', this.locale)
    },
    async loadBootstrap() {
      try {
        this.bootstrap = await fetchBootstrap()
      } catch (err) {
        console.warn('bootstrap failed', err)
      }
    },
    startTraining() {
      uni.navigateTo({ url: '/pages/realtime/realtime' })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 24rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top right, var(--hero-glow), transparent 30%),
    radial-gradient(circle at left center, var(--hero-glow-alt), transparent 24%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(78rpx);
}

.ambient-top {
  width: 260rpx;
  height: 260rpx;
  right: -120rpx;
  top: 180rpx;
  background: var(--hero-glow);
}

.ambient-side {
  width: 220rpx;
  height: 220rpx;
  left: -90rpx;
  bottom: 240rpx;
  background: var(--hero-glow-alt);
}

.module-list,
.insight-card {
  position: relative;
  z-index: 2;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  margin-bottom: 26rpx;
  padding-top: 12rpx;
}

.module-card {
  position: relative;
  height: 340rpx;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.module-image,
.module-mask {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.module-mask {
  background: linear-gradient(180deg, rgba(8, 10, 18, 0.08) 0%, rgba(8, 10, 18, 0.84) 100%);
}

.module-info {
  position: absolute;
  left: 26rpx;
  right: 26rpx;
  bottom: 24rpx;
  color: #ffffff;
}

.module-top {
  display: flex;
}

.module-tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.16);
  font-size: 20rpx;
}

.module-title {
  display: block;
  margin-top: 14rpx;
  font-size: 44rpx;
  font-weight: 700;
}

.module-copy {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.54;
  color: rgba(255, 255, 255, 0.82);
}

.module-btn {
  margin-top: 18rpx;
  width: 220rpx;
  height: 78rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: rgba(255, 255, 255, 0.18);
  border: 1rpx solid rgba(255, 255, 255, 0.32);
  backdrop-filter: blur(16rpx);
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 700;
}

.module-btn::after {
  border: none;
}

.insight-card {
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.section-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.insight-title {
  display: block;
  margin-top: 12rpx;
  font-size: 40rpx;
  line-height: 1.22;
  font-weight: 700;
}

.insight-text {
  display: block;
  margin-top: 14rpx;
  font-size: 25rpx;
  line-height: 1.66;
  color: var(--text-secondary);
}
</style>
