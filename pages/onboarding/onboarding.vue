<template>
  <view class="container bg-background">
    <!-- Top Navigation -->
    <header class="header">
      <div class="header-spacer"></div>
      <h1 class="app-title">AuraPose</h1>
      <div class="header-spacer"></div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Hero Section -->
      <div class="hero-section">
        <h2 class="hero-title">
          开启您的 <span class="text-primary">AI</span> 健身之旅
        </h2>
        <p class="hero-subtitle">
          输入您的基础信息，让 AI 为您定制专属方案
        </p>
      </div>

      <!-- AI Kinetic Sphere -->
      <div class="ai-sphere-container">
        <div class="ai-sphere-bg"></div>
        <div class="glass-panel ai-sphere">
          <text class="material-symbols-outlined ai-icon"></text>
        </div>
      </div>

      <!-- Onboarding Form -->
      <div class="form-container">
        <!-- Gender Selection -->
        <section class="form-section">
          <label class="form-label">性别 (Gender)</label>
          <div class="gender-grid">
            <button class="glass-panel gender-btn" :class="{ active: gender === 'male' }" @click="selectGender('male')">
              <text class="material-symbols-outlined gender-icon">male</text>
              <span class="gender-text">男</span>
            </button>
            <button class="glass-panel gender-btn" :class="{ active: gender === 'female' }" @click="selectGender('female')">
              <text class="material-symbols-outlined gender-icon">female</text>
              <span class="gender-text">女</span>
            </button>
          </div>
        </section>

        <!-- Age Selection -->
        <section class="glass-panel age-section">
          <div class="age-header">
            <label class="form-label">年龄 (Age)</label>
            <span class="age-value">{{ age }} <span class="age-unit">岁</span></span>
          </div>
          <div class="slider-container">
            <div class="slider-track"></div>
            <div class="slider-progress" :style="{ width: agePercentage + '%' }"></div>
            <div class="slider-thumb" :style="{ left: agePercentage + '%' }" @touchstart="startDrag" @touchmove="drag" @touchend="endDrag"></div>
          </div>
        </section>

        <!-- Physical Specs -->
        <div class="specs-grid">
          <!-- Height -->
          <div class="glass-panel spec-item">
            <label class="form-label">身高 (Height)</label>
            <div class="spec-input">
              <input type="number" v-model="height" class="spec-input-field" />
              <span class="spec-unit">cm</span>
            </div>
          </div>
          <!-- Weight -->
          <div class="glass-panel spec-item">
            <label class="form-label">体重 (Weight)</label>
            <div class="spec-input">
              <input type="number" v-model="weight" class="spec-input-field" />
              <span class="spec-unit">kg</span>
            </div>
          </div>
        </div>


      </div>

      <!-- Action Button -->
      <div class="action-button-container">
        <button class="action-button" @click="generatePlan">
          <span>生成我的方案</span>
        </button>
        <p class="privacy-text">您的数据受端到端加密保护</p>
      </div>
    </main>
  </view>
</template>

<script>
import { saveProfile } from '../../common/api.js'

export default {
  data() {
    return {
      gender: 'male',
      age: 28,
      height: 180,
      weight: 75,
      isDragging: false
    }
  },
  computed: {
    agePercentage() {
      return (this.age / 100) * 100;
    }
  },
  methods: {
    selectGender(gender) {
      this.gender = gender;
    },
    startDrag() {
      this.isDragging = true;
    },
    drag(event) {
      if (!this.isDragging) return;
      if (!event.currentTarget || !event.currentTarget.parentElement) return;
      const slider = event.currentTarget.parentElement;
      const rect = slider.getBoundingClientRect();
      if (!rect) return;
      let percentage = (event.touches[0].clientX - rect.left) / rect.width;
      percentage = Math.max(0, Math.min(1, percentage));
      this.age = Math.round(percentage * 100);
    },
    endDrag() {
      this.isDragging = false;
    },
    async generatePlan() {
      try {
        await saveProfile({
          gender: this.gender,
          age: this.age,
          height: this.height,
          weight: this.weight
        });
      } catch (err) {
        uni.showToast({
          title: `保存失败: ${err}`,
          icon: 'none'
        });
      }
      // 跳转到主页
      uni.switchTab({ url: '/pages/home/home' });
    },
    goBack() {
      uni.navigateBack();
    }
  }
}
</script>

<style>
/* 全局样式 */
.container {
  min-height: 100vh;
  background-color: #0e0e0e;
  color: #ffffff;
  font-family: 'Plus Jakarta Sans', sans-serif;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

/* 顶部导航 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 60rpx;
  background: rgba(14, 14, 14, 0.8);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(142, 171, 255, 0.1);
}

.nav-btn {
  color: #8eabff;
  background: none;
  border: none;
  font-size: 24px;
}

.header-spacer {
  width: 24px;
}

.app-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(90deg, #8eabff, #bc87fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 主内容 */
.main-content {
  padding: 60rpx;
}

/* 英雄区域 */
.hero-section {
  text-align: center;
  margin-bottom: 80rpx;
}

.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 60rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.text-primary {
  color: #8eabff;
}

.hero-subtitle {
  font-size: 28rpx;
  color: #adaaaa;
  padding: 0 40rpx;
}

/* AI 球体 */
.ai-sphere-container {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 80rpx;
}

.ai-sphere-bg {
  position: absolute;
  width: 384rpx;
  height: 384rpx;
  background-color: rgba(160, 255, 240, 0.2);
  border-radius: 50%;
  filter: blur(120rpx);
}

.ai-sphere {
  position: relative;
  z-index: 10;
  width: 192rpx;
  height: 192rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(160, 255, 240, 0.3);
}

.ai-icon {
  font-size: 80rpx;
  color: #a0fff0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 表单容器 */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 48rpx;
}

.form-section {
  margin-bottom: 32rpx;
}

.form-label {
  display: block;
  font-size: 24rpx;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 4rpx;
  color: #adaaaa;
  margin-bottom: 32rpx;
}

/* 性别选择 */
.gender-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32rpx;
}

.gender-btn {
  padding: 48rpx;
  border-radius: 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  transition: all 0.3s ease;
}

.gender-btn.active {
  border: 1px solid rgba(142, 171, 255, 0.4);
  background-color: #262626;
}

.gender-btn:not(.active) {
  opacity: 0.6;
}

.gender-icon {
  font-size: 60rpx;
}

.gender-btn.active .gender-icon {
  color: #8eabff;
}

.gender-btn:not(.active) .gender-icon {
  color: #bc87fe;
}

.gender-text {
  font-weight: bold;
  color: #ffffff;
  font-size: 32rpx;
}

/* 年龄选择 */
.age-section {
  padding: 48rpx;
  border-radius: 24rpx;
}

.age-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.age-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 48rpx;
  font-weight: bold;
  color: #8eabff;
}

.age-unit {
  font-size: 24rpx;
  font-weight: normal;
  color: #adaaaa;
  margin-left: 8rpx;
}

.slider-container {
  position: relative;
  height: 96rpx;
  display: flex;
  align-items: center;
}

.slider-track {
  position: absolute;
  width: 100%;
  height: 8rpx;
  background-color: #262626;
  border-radius: 4rpx;
}

.slider-progress {
  position: absolute;
  height: 8rpx;
  background: linear-gradient(90deg, #8eabff, #bc87fe);
  border-radius: 4rpx;
}

.slider-thumb {
  position: absolute;
  width: 40rpx;
  height: 40rpx;
  background-color: #ffffff;
  border: 8rpx solid #8eabff;
  border-radius: 50%;
  transform: translateX(-50%);
  box-shadow: 0 0 30rpx rgba(142, 171, 255, 0.5);
  cursor: pointer;
}

/* 身体数据 */
.specs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32rpx;
}

.spec-item {
  padding: 48rpx;
  border-radius: 24rpx;
}

.spec-input {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
}

.spec-input-field {
  background: transparent;
  border: none;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 48rpx;
  font-weight: bold;
  color: #ffffff;
  width: 160rpx;
  outline: none;
}

.spec-unit {
  font-size: 24rpx;
  font-weight: medium;
  color: #a0fff0;
}

.spec-item:nth-child(2) .spec-unit {
  color: #bc87fe;
}

/* 可视化 */
.visualization {
  position: relative;
  height: 128px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.visualization-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.2;
  mix-blend-mode: overlay;
}

.visualization-content {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 0 24px;
}

.pulse-bars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
}

.pulse-bar {
  width: 4px;
  border-radius: 2px;
  animation: pulse 1.5s infinite;
}

.bar-1 {
  height: 16px;
  background-color: #a0fff0;
  animation-delay: 0s;
}

.bar-2 {
  height: 24px;
  background-color: #8eabff;
  animation-delay: 0.2s;
}

.bar-3 {
  height: 12px;
  background-color: #bc87fe;
  animation-delay: 0.4s;
}

.visualization-text {
  font-size: 10px;
  font-weight: medium;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #adaaaa;
}

/* 操作按钮 */
.action-button-container {
  width: 100%;
  margin-top: 96rpx;
}

.action-button {
  width: 100%;
  background: linear-gradient(90deg, #8eabff, #156aff);
  color: #002971;
  font-weight: bold;
  padding: 40rpx;
  border-radius: 9999rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 16rpx 60rpx rgba(21, 106, 255, 0.4);
  transition: all 0.3s ease;
  font-size: 32rpx;
}

.action-button:hover {
  opacity: 0.9;
}

.action-button:active {
  transform: scale(0.95);
}

.action-icon {
  font-size: 40rpx;
}

.privacy-text {
  text-align: center;
  font-size: 20rpx;
  color: #adaaaa;
  margin-top: 32rpx;
  opacity: 0.5;
}

/* 玻璃面板样式 */
.glass-panel {
  background: rgba(38, 38, 38, 0.4);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(142, 171, 255, 0.1);
}

/* 背景网格 */
.bg-mesh {
  background: radial-gradient(circle at 10% 20%, rgba(142, 171, 255, 0.1) 0%, transparent 40%),
              radial-gradient(circle at 90% 80%, rgba(188, 135, 254, 0.1) 0%, transparent 40%);
}
</style>
