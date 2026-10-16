<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-top"></view>
    <view class="ambient ambient-bottom"></view>

    <view class="hero">
      <text class="hero-kicker">{{ copy.heroKicker }}</text>
      <text class="hero-title">{{ copy.heroTitle }}</text>
      <text class="hero-subtitle">{{ copy.heroSubtitle }}</text>
    </view>

    <view class="crop-panel">
      <view
        class="crop-stage"
        @touchstart="handleTouchStart"
        @touchmove.stop.prevent="handleTouchMove"
        @touchend="handleTouchEnd"
        @touchcancel="handleTouchEnd"
      >
        <image
          v-if="sourcePath"
          class="crop-image"
          :src="sourcePath"
          mode="aspectFill"
          :style="imageStyle"
        />
        <view class="mask-ring"></view>
        <view class="mask-corners mask-top-left"></view>
        <view class="mask-corners mask-top-right"></view>
        <view class="mask-corners mask-bottom-left"></view>
        <view class="mask-corners mask-bottom-right"></view>
      </view>

      <view class="zoom-panel">
        <text class="zoom-label">{{ copy.zoomLabel }}</text>
        <slider
          class="zoom-slider"
          :value="zoomPercent"
          :min="100"
          :max="220"
          :block-size="20"
          :activeColor="themeMode === 'light' ? '#4c6fff' : '#9cb3ff'"
          :backgroundColor="themeMode === 'light' ? '#d7dfee' : '#24304f'"
          @changing="handleZoomChange"
          @change="handleZoomChange"
        />
      </view>

      <view class="action-row">
        <button class="ghost-btn" @click="resetFrame">{{ copy.reset }}</button>
        <button class="confirm-btn" :loading="saving" @click="confirmCrop">{{ copy.confirm }}</button>
      </view>
    </view>

    <canvas
      canvas-id="avatarCropCanvas"
      class="export-canvas"
      :style="{ width: `${canvasSize}px`, height: `${canvasSize}px` }"
    ></canvas>
  </view>
</template>

<script>
import {
  applyNativeTheme,
  getThemeClass,
  getThemeMode,
  getThemeVars,
  mergeStoredProfile
} from '../../common/theme.js'
import { applyPageLocale, getCopy, getLocale } from '../../common/i18n.js'

export default {
  data() {
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      sourcePath: '',
      imageInfo: null,
      stageSize: 0,
      canvasSize: 640,
      imageScale: 1.18,
      baseScale: 1,
      offsetX: 0,
      offsetY: 0,
      startTouch: null,
      saving: false
    }
  },
  computed: {
    copy() {
      return getCopy('avatarCrop', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    zoomPercent() {
      return Math.round(this.imageScale * 100)
    },
    imageStyle() {
      if (!this.imageInfo || !this.stageSize) {
        return ''
      }

      const width = this.getRenderedWidth()
      const height = this.getRenderedHeight()
      const left = (this.stageSize - width) / 2 + this.offsetX
      const top = (this.stageSize - height) / 2 + this.offsetY

      return `width:${width}px;height:${height}px;left:${left}px;top:${top}px;`
    }
  },
  onLoad(options) {
    this.sourcePath = decodeURIComponent(options.src || '')
    this.stageSize = uni.upx2px(560)
    this.syncTheme()
    this.syncLocale()
    this.loadImageInfo()
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
      applyPageLocale('avatarCrop', this.locale)
    },
    loadImageInfo() {
      if (!this.sourcePath) {
        return
      }

      uni.getImageInfo({
        src: this.sourcePath,
        success: (res) => {
          this.imageInfo = res
          this.fitImage()
        },
        fail: () => {
          uni.showToast({
            title: this.copy.imageReadFailed,
            icon: 'none'
          })
        }
      })
    },
    fitImage() {
      if (!this.imageInfo || !this.stageSize) {
        return
      }

      const { width, height } = this.imageInfo
      this.baseScale = Math.max(this.stageSize / width, this.stageSize / height)
      this.imageScale = 1.18
      this.offsetX = 0
      this.offsetY = 0
      this.clampOffset()
    },
    getRenderedWidth(scale = this.imageScale) {
      return this.imageInfo.width * this.baseScale * scale
    },
    getRenderedHeight(scale = this.imageScale) {
      return this.imageInfo.height * this.baseScale * scale
    },
    clampOffset() {
      if (!this.imageInfo || !this.stageSize) {
        return
      }

      const width = this.getRenderedWidth()
      const height = this.getRenderedHeight()
      const maxOffsetX = Math.max(0, (width - this.stageSize) / 2)
      const maxOffsetY = Math.max(0, (height - this.stageSize) / 2)

      this.offsetX = Math.min(maxOffsetX, Math.max(-maxOffsetX, this.offsetX))
      this.offsetY = Math.min(maxOffsetY, Math.max(-maxOffsetY, this.offsetY))
    },
    handleTouchStart(event) {
      const touch = (event.touches && event.touches[0]) || null
      if (!touch) {
        return
      }

      this.startTouch = {
        x: touch.clientX,
        y: touch.clientY,
        offsetX: this.offsetX,
        offsetY: this.offsetY
      }
    },
    handleTouchMove(event) {
      if (!this.startTouch) {
        return
      }

      const touch = (event.touches && event.touches[0]) || null
      if (!touch) {
        return
      }

      this.offsetX = this.startTouch.offsetX + (touch.clientX - this.startTouch.x)
      this.offsetY = this.startTouch.offsetY + (touch.clientY - this.startTouch.y)
      this.clampOffset()
    },
    handleTouchEnd() {
      this.startTouch = null
    },
    handleZoomChange(event) {
      this.imageScale = Math.max(1, Number(event.detail.value || 100) / 100)
      this.clampOffset()
    },
    resetFrame() {
      this.fitImage()
    },
    confirmCrop() {
      if (!this.sourcePath || !this.imageInfo || this.saving) {
        return
      }

      this.saving = true
      const exportSize = this.canvasSize
      const ctx = uni.createCanvasContext('avatarCropCanvas', this)
      const width = this.getRenderedWidth()
      const height = this.getRenderedHeight()
      const left = (this.stageSize - width) / 2 + this.offsetX
      const top = (this.stageSize - height) / 2 + this.offsetY
      const scaleRatio = exportSize / this.stageSize

      ctx.clearRect(0, 0, exportSize, exportSize)
      ctx.save()
      ctx.beginPath()
      ctx.arc(exportSize / 2, exportSize / 2, exportSize / 2, 0, Math.PI * 2)
      ctx.clip()
      ctx.drawImage(
        this.sourcePath,
        left * scaleRatio,
        top * scaleRatio,
        width * scaleRatio,
        height * scaleRatio
      )
      ctx.restore()

      ctx.draw(false, async () => {
        try {
          const tempPath = await this.exportCanvas()
          const savedPath = await this.persistAvatar(tempPath)
          mergeStoredProfile({ avatarPath: savedPath })
          uni.navigateBack()
        } catch (err) {
          uni.showToast({
            title: this.copy.avatarGenerateFailed,
            icon: 'none'
          })
        } finally {
          this.saving = false
        }
      })
    },
    exportCanvas() {
      return new Promise((resolve, reject) => {
        uni.canvasToTempFilePath(
          {
            canvasId: 'avatarCropCanvas',
            x: 0,
            y: 0,
            width: this.canvasSize,
            height: this.canvasSize,
            destWidth: this.canvasSize,
            destHeight: this.canvasSize,
            fileType: 'png',
            success: (res) => resolve(res.tempFilePath),
            fail: reject
          },
          this
        )
      })
    },
    persistAvatar(tempFilePath) {
      return new Promise((resolve) => {
        uni.saveFile({
          tempFilePath,
          success: (res) => resolve(res.savedFilePath || tempFilePath),
          fail: () => resolve(tempFilePath)
        })
      })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 40rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top left, var(--hero-glow), transparent 34%),
    radial-gradient(circle at bottom right, var(--hero-glow-alt), transparent 28%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(68rpx);
  opacity: 0.8;
}

.ambient-top {
  width: 260rpx;
  height: 260rpx;
  top: 200rpx;
  right: -80rpx;
  background: var(--hero-glow);
}

.ambient-bottom {
  width: 280rpx;
  height: 280rpx;
  left: -120rpx;
  bottom: 140rpx;
  background: var(--hero-glow-alt);
}

.hero,
.crop-panel {
  position: relative;
  z-index: 2;
}

.hero {
  margin-bottom: 32rpx;
}

.hero-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  color: var(--text-muted);
  text-transform: uppercase;
}

.hero-title {
  display: block;
  margin-top: 14rpx;
  font-size: 58rpx;
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

.crop-panel {
  padding: 30rpx;
  border-radius: 36rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18rpx);
}

.crop-stage {
  position: relative;
  width: 560rpx;
  height: 560rpx;
  margin: 0 auto;
  border-radius: 36rpx;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(18, 32, 51, 0.1), rgba(18, 32, 51, 0.04)),
    var(--surface-strong);
}

.crop-image {
  position: absolute;
}

.mask-ring {
  position: absolute;
  inset: 40rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.95);
  box-shadow:
    0 0 0 999rpx rgba(7, 14, 28, 0.34),
    inset 0 0 0 1rpx rgba(255, 255, 255, 0.35);
  pointer-events: none;
}

.mask-corners {
  position: absolute;
  width: 48rpx;
  height: 48rpx;
  border-color: rgba(255, 255, 255, 0.9);
  border-style: solid;
  pointer-events: none;
}

.mask-top-left {
  top: 28rpx;
  left: 28rpx;
  border-width: 4rpx 0 0 4rpx;
  border-top-left-radius: 18rpx;
}

.mask-top-right {
  top: 28rpx;
  right: 28rpx;
  border-width: 4rpx 4rpx 0 0;
  border-top-right-radius: 18rpx;
}

.mask-bottom-left {
  left: 28rpx;
  bottom: 28rpx;
  border-width: 0 0 4rpx 4rpx;
  border-bottom-left-radius: 18rpx;
}

.mask-bottom-right {
  right: 28rpx;
  bottom: 28rpx;
  border-width: 0 4rpx 4rpx 0;
  border-bottom-right-radius: 18rpx;
}

.zoom-panel {
  margin-top: 26rpx;
}

.zoom-label {
  display: block;
  font-size: 24rpx;
  color: var(--text-muted);
  margin-bottom: 10rpx;
}

.zoom-slider {
  margin: 0;
}

.action-row {
  display: flex;
  gap: 14rpx;
  margin-top: 22rpx;
}

.ghost-btn,
.confirm-btn {
  flex: 1;
  height: 92rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 700;
  padding: 0;
}

.ghost-btn {
  background: var(--surface-strong);
  color: var(--text);
  border: 1rpx solid var(--border);
}

.confirm-btn {
  background: linear-gradient(135deg, var(--brand), var(--brand-soft));
  color: #ffffff;
  box-shadow: var(--shadow);
}

.ghost-btn::after,
.confirm-btn::after {
  border: none;
}

.export-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
  opacity: 0;
  pointer-events: none;
}
</style>
