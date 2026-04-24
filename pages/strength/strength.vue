<template>
  <view class="container bg-background">
    <!-- Top Navigation -->
    <header class="header">
      <div class="header-content">
        <button class="menu-btn">
          <text class="material-symbols-outlined">menu</text>
        </button>
        <h1 class="page-title">力量训练</h1>
        <div class="user-avatar">
          <img src="/static/logo.png" alt="用户头像" class="avatar-image" />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- AI Stats Pulse Header -->
      <div class="ai-stats-card ai-pulse">
        <div class="ai-stats-content">
          <div class="ai-stats-text">
            <p class="ai-stats-label">AI 实时体能评估</p>
            <p class="ai-stats-value">92% <span class="ai-stats-unit">状态极佳</span></p>
          </div>
          <div class="ai-stats-indicator">
            <p class="ai-indicator-text">AI KINETIC ACTIVE</p>
          </div>
        </div>
        <!-- Kinetic Sphere Background Deco -->
        <div class="kinetic-sphere-deco"></div>
      </div>

      <!-- Training Modules: Bento-inspired Grid -->
      <div class="training-modules">
        <!-- Module: 弯举 -->
        <div class="module-card glass-card">
          <div class="module-image-container">
            <img src="/static/logo.png" alt="弯举" class="module-image" />

            <div class="ai-tracking-badge">
              <p class="ai-tracking-text">AI 追踪中</p>
            </div>
          </div>
          <div class="module-info">
            <div class="module-header">
              <div class="module-title-section">
                <h3 class="module-title">弯举</h3>
                <p class="module-target">目标: <span class="module-target-muscle primary">肱二头肌</span></p>
              </div>
              <div class="module-recommendation">
                <p class="module-recommendation-label">推荐重量</p>
                <p class="module-recommendation-value secondary">12.5 KG</p>
              </div>
            </div>
            <button class="module-start-btn" @click="startTraining">
              <span>开始训练</span>
            </button>
          </div>
        </div>

        <!-- Module: 仰卧起坐 -->
        <div class="module-card glass-card">
          <div class="module-image-container">
            <img src="/static/logo.png" alt="仰卧起坐" class="module-image" />
            <div class="module-gradient"></div>
            <div class="module-progress-bar">
              <div class="module-progress-fill tertiary"></div>
            </div>
          </div>
          <div class="module-info">
            <div class="module-header">
              <div class="module-title-section">
                <h3 class="module-title">仰卧起坐</h3>
                <p class="module-target">目标: <span class="module-target-muscle tertiary">核心肌群</span></p>
              </div>
              <div class="module-recommendation">
                <p class="module-recommendation-label">今日目标</p>
                <p class="module-recommendation-value tertiary">50 次</p>
              </div>
            </div>
            <button class="module-start-btn" @click="startTraining">
              <span>开始训练</span>
            </button>
          </div>
        </div>

        <!-- Module: 引体向上 -->
        <div class="module-card glass-card">
          <div class="module-image-container">
            <img src="/static/logo.png" alt="引体向上" class="module-image" />
            <div class="module-star">
              <text class="material-symbols-outlined">stars</text>
            </div>
          </div>
          <div class="module-info">
            <div class="module-header">
              <div class="module-title-section">
                <h3 class="module-title">引体向上</h3>
                <p class="module-target">目标: <span class="module-target-muscle secondary">背部肌群</span></p>
              </div>
              <div class="module-recommendation">
                <p class="module-recommendation-label">难度</p>
                <p class="module-recommendation-value secondary">高级</p>
              </div>
            </div>
            <button class="module-start-btn" @click="startTraining">
              <span>开始训练</span>
            </button>
          </div>
        </div>

        <!-- Module: 深蹲 -->
        <div class="module-card glass-card">
          <div class="module-image-container">
            <img src="/static/logo.png" alt="深蹲" class="module-image" />
            <div class="module-calibration">
              <p class="module-calibration-text">AI 正在校准关节角度...</p>
            </div>
          </div>
          <div class="module-info">
            <div class="module-header">
              <div class="module-title-section">
                <h3 class="module-title">深蹲</h3>
                <p class="module-target">目标: <span class="module-target-muscle primary">腿部肌群</span></p>
              </div>
              <div class="module-recommendation">
                <p class="module-recommendation-label">推荐负重</p>
                <p class="module-recommendation-value primary">45 KG</p>
              </div>
            </div>
            <button class="module-start-btn" @click="startTraining">
              <span>开始训练</span>
            </button>
          </div>
        </div>
      </div>

      <!-- AI Kinetic Insight (Bonus Component) -->
      <div class="ai-insight-card glass-card">
        <div class="ai-insight-content">
          <div class="ai-insight-text">
            <h4 class="ai-insight-title">AI 建议</h4>
            <p class="ai-insight-description">根据你今早的恢复数据，建议将“深蹲”训练组间休息延长至 90 秒，以最大化肌肉泵感。</p>
          </div>
        </div>
      </div>
    </main>


  </view>
</template>

<script>
import { fetchBootstrap } from '../../common/api.js'

export default {
  data() {
    return {
      bootstrap: null,
      // 页面数据
    }
  },
  onLoad() {
    this.loadBootstrap()
  },
  methods: {
    async loadBootstrap() {
      try {
        this.bootstrap = await fetchBootstrap()
      } catch (err) {
        console.warn('bootstrap failed', err)
      }
    },
    startTraining() {
      uni.navigateTo({ url: '/pages/realtime/realtime' });
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
}

/* 顶部导航 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  background: rgba(14, 14, 14, 0.8);
  backdrop-filter: blur(24px);
  background: linear-gradient(to bottom, #1a1a1a, transparent);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  max-width: 2xl;
  margin: 0 auto;
}

.menu-btn {
  background: none;
  border: none;
  color: #8eabff;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-btn:active {
  transform: scale(0.95);
}

.page-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: bold;
  color: #8eabff;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #262626;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.user-avatar:active {
  transform: scale(0.95);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 主内容 */
.main-content {
  padding: 96px 30px 32px;
  max-width: 2xl;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* AI 状态卡片 */
.ai-stats-card {
  position: relative;
  padding: 24px;
  border-radius: 24px;
  background-color: #131313;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.ai-pulse {
  box-shadow: 0 0 20px rgba(142, 171, 255, 0.2);
}

.ai-stats-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  position: relative;
  z-index: 10;
}

.ai-stats-label {
  font-size: 12px;
  font-weight: medium;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #adaaaa;
  margin-bottom: 4px;
}

.ai-stats-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 30px;
  font-weight: bold;
  color: #a0fff0;
}

.ai-stats-unit {
  font-size: 14px;
  font-weight: normal;
  color: #adaaaa;
  letter-spacing: normal;
}

.ai-stats-indicator {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.ai-indicator-icon {
  font-size: 24px;
  color: #bc87fe;
  animation: pulse 2s infinite;
}

.ai-indicator-text {
  font-size: 10px;
  font-weight: bold;
  letter-spacing: -0.5px;
  color: #bc87fe;
}

.kinetic-sphere-deco {
  position: absolute;
  right: -48px;
  top: -48px;
  width: 128px;
  height: 128px;
  background-color: rgba(160, 255, 240, 0.1);
  border-radius: 50%;
  filter: blur(48px);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 训练模块 */
.training-modules {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.module-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.module-card:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.module-image-container {
  position: relative;
  aspect-ratio: 4/3;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
  background-color: #262626;
}

.module-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.8;
  transition: transform 0.5s ease;
}

.module-card:hover .module-image {
  transform: scale(1.05);
}



.ai-tracking-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background-color: rgba(142, 171, 255, 0.2);
  backdrop-filter: blur(12px);
  padding: 4px 12px;
  border-radius: 9999px;
}

.ai-tracking-text {
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 1px;
  color: #8eabff;
}

.module-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6), transparent);
}

.module-progress-bar {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  height: 4px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.module-progress-fill {
  height: 100%;
  border-radius: 2px;
}

.module-progress-fill.tertiary {
  background-color: #a0fff0;
  box-shadow: 0 0 8px rgba(160, 255, 240, 0.6);
  width: 66.67%;
}

.module-star {
  position: absolute;
  top: 12px;
  right: 12px;
}

.module-star .material-symbols-outlined {
  font-size: 24px;
  color: #bc87fe;
  font-variation-settings: 'FILL' 1;
}

.module-calibration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
}

.module-calibration-text {
  font-size: 10px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.7);
}

.module-info {
  padding: 20px;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.module-title-section {
  flex: 1;
}

.module-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 4px;
}

.module-target {
  font-size: 12px;
  color: #adaaaa;
  font-weight: medium;
}

.module-target-muscle {
  font-weight: normal;
}

.module-target-muscle.primary {
  color: #8eabff;
}

.module-target-muscle.secondary {
  color: #bc87fe;
}

.module-target-muscle.tertiary {
  color: #a0fff0;
}

.module-recommendation {
  text-align: right;
}

.module-recommendation-label {
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #adaaaa;
  margin-bottom: 4px;
}

.module-recommendation-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 16px;
  font-weight: bold;
}

.module-recommendation-value.primary {
  color: #8eabff;
}

.module-recommendation-value.secondary {
  color: #bc87fe;
}

.module-recommendation-value.tertiary {
  color: #a0fff0;
}

.module-start-btn {
  width: 100%;
  background-color: #8eabff;
  color: #002971;
  font-weight: bold;
  padding: 12px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.module-start-btn:active {
  transform: scale(0.95);
}

.module-start-btn .material-symbols-outlined {
  font-size: 16px;
  color: #002971;
}

/* AI 洞察卡片 */
.ai-insight-card {
  border-radius: 24px;
  padding: 24px;
  border-left: 4px solid #a0fff0;
}

.ai-insight-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.ai-insight-icon {
  padding: 8px;
  background-color: rgba(160, 255, 240, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-insight-icon .material-symbols-outlined {
  font-size: 24px;
  color: #a0fff0;
}

.ai-insight-title {
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 4px;
}

.ai-insight-description {
  font-size: 14px;
  line-height: 1.4;
  color: #adaaaa;
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 12px 20px 24px;
  background: rgba(14, 14, 14, 0.9);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 50;
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.5);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4px 16px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.nav-item.active {
  background-color: rgba(142, 171, 255, 0.1);
  border-radius: 16px;
  color: #8eabff;
}

.nav-item:not(.active) {
  color: #565555;
}

.nav-item:hover:not(.active) {
  color: #bc87fe;
}

.nav-item .material-symbols-outlined {
  font-size: 24px;
  margin-bottom: 4px;
}

.nav-item.active .material-symbols-outlined {
  font-variation-settings: 'FILL' 1;
}

.nav-label {
  font-size: 10px;
  font-weight: medium;
  letter-spacing: 1px;
}

/* 玻璃面板样式 */
.glass-card {
  background: rgba(26, 26, 26, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
