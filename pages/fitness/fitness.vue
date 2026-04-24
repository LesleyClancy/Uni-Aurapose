<template>
  <view class="container bg-background">
    <!-- Top Navigation -->
    <header class="header">
      <div class="header-content">
        <div class="app-logo">
          <span class="app-title">AuraPose</span>
        </div>
        
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- AI Kinetic Sphere Background Decoration -->
      <div class="kinetic-sphere kinetic-sphere-1"></div>
      <div class="kinetic-sphere kinetic-sphere-2"></div>

      <!-- Section: Categories (Bento Grid Style) -->
      <section class="categories-section">
        <h2 class="section-title">运动类别</h2>
        <div class="categories-grid">
          <div class="category-card primary" @click="navigateToStrength">
            <div class="category-icon">
              <text class="material-symbols-outlined">fitness_center</text>
            </div>
            <span class="category-name">力量训练</span>
          </div>
          <div class="category-card secondary">
            <div class="category-icon">
              <text class="material-symbols-outlined">directions_run</text>
            </div>
            <span class="category-name">有氧训练</span>
          </div>
          <div class="category-card tertiary">
            <div class="category-icon">
              <text class="material-symbols-outlined">self_improvement</text>
            </div>
            <span class="category-name">无氧训练</span>
          </div>
          <div class="category-card special">
            <div class="category-gradient"></div>
            <div class="category-icon special">
              <text class="material-symbols-outlined">psychology</text>
            </div>
            <span class="category-name">ai测评</span>
          </div>
        </div>
      </section>

      <!-- Section: Continue Training -->
      <section class="continue-section">
        <div class="continue-card glass-card">
          <div class="continue-content">
            <span class="continue-badge">继续训练</span>
            <h3 class="continue-title">全身燃脂挑战</h3>
            <div class="continue-progress">
              <div class="progress-info">
                <span class="progress-percentage">45<span class="progress-unit">%</span></span>
                <p class="progress-label">已完成进度</p>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar">
                  <div class="progress-fill" style="width: 45%"></div>
                </div>
              </div>
            </div>
            <button class="continue-btn">
              <span>恢复训练</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Section: Course List (Asymmetric Layout) -->
      <section class="courses-section">
        <div class="courses-header">
          <div>
            <h2 class="section-title">为你推荐</h2>
            <p class="section-subtitle">基于您的身体数据与近期目标</p>
          </div>
          <button class="view-all-btn">查看全部</button>
        </div>
        <div class="courses-grid">
          <!-- Course Card 1 -->
          <div class="course-card">
            <div class="course-image-container">
              <img src="/static/logo.png" alt="Strength Training" class="course-image" />
              <div class="course-gradient"></div>
              <div class="course-meta">
                <span class="course-difficulty">中等强度</span>
                <span class="course-duration">
                  <text class="material-symbols-outlined">schedule</text> 35 分钟
                </span>
              </div>
            </div>
            <h4 class="course-title">高强度核心爆发</h4>
            <p class="course-description">专注于腹肌与核心稳定性的力量练习</p>
          </div>

          <!-- Course Card 2 -->
          <div class="course-card">
            <div class="course-image-container">
              <img src="/static/logo.png" alt="Yoga Session" class="course-image" />
              <div class="course-gradient"></div>
              <div class="course-meta">
                <span class="course-difficulty">低强度</span>
                <span class="course-duration">
                  <text class="material-symbols-outlined">schedule</text> 20 分钟
                </span>
              </div>
            </div>
            <h4 class="course-title">晚间深度拉伸</h4>
            <p class="course-description">缓解全天疲劳，促进深度睡眠的瑜伽课程</p>
          </div>

          <!-- Course Card 3 (Bento-like smaller horizontal) -->
          <div class="course-card horizontal">
            <div class="course-image-container horizontal">
              <img src="/static/logo.png" alt="HIIT" class="course-image" />
            </div>
            <div class="course-content horizontal">
              <div class="course-badge-container">
                <span class="course-badge">限时挑战</span>
              </div>
              <h4 class="course-title">HIIT 极速燃脂</h4>
              <p class="course-description">通过短时间高强度爆发，提升您的基础代谢率。</p>
              <div class="course-stats">
                <span class="course-stat">
                  450 千卡
                </span>
                <span class="course-stat">
                  <text class="material-symbols-outlined">schedule</text> 15 分钟
                </span>
              </div>
            </div>
            <div class="course-arrow">
              <div class="arrow-circle">
                <text class="material-symbols-outlined">chevron_right</text>
              </div>
            </div>
          </div>
        </div>
      </section>
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
    navigateToStrength() {
      uni.navigateTo({ url: '/pages/strength/strength' });
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
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: #0e0e0e;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  max-width: 7xl;
  margin: 0 auto;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.app-logo:active {
  transform: scale(0.95);
}

.logo-icon {
  font-size: 24px;
  color: #8eabff;
}

.app-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(90deg, #8eabff, #bc87fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.camera-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(142, 171, 255, 0.2);
  background-color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.camera-btn:active {
  transform: scale(0.95);
}

.camera-btn .material-symbols-outlined {
  font-size: 20px;
  color: #8eabff;
  font-variation-settings: 'FILL' 1;
}

/* 主内容 */
.main-content {
  padding: 24px 30px;
  position: relative;
  max-width: 7xl;
  margin: 0 auto;
}

/* 动力学球体装饰 */
.kinetic-sphere {
  position: fixed;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.15;
  z-index: -10;
}

.kinetic-sphere-1 {
  top: 25%;
  right: 0;
  width: 256px;
  height: 256px;
  background: radial-gradient(circle at 30% 30%, #a0fff0 0%, #8eabff 50%, #bc87fe 100%);
}

.kinetic-sphere-2 {
  bottom: 25%;
  left: 0;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle at 30% 30%, #a0fff0 0%, #8eabff 50%, #bc87fe 100%);
  opacity: 0.1;
}

/* 类别部分 */
.categories-section {
  margin-bottom: 40px;
}

.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 24px;
  letter-spacing: -0.5px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.category-card {
  background-color: #20201f;
  padding: 24px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.category-card:hover {
  transform: translateY(-2px);
}

.category-card.primary:hover {
  background-color: rgba(142, 171, 255, 0.1);
}

.category-card.secondary:hover {
  background-color: rgba(188, 135, 254, 0.1);
}

.category-card.tertiary:hover {
  background-color: rgba(160, 255, 240, 0.1);
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.category-card:hover .category-icon {
  transform: scale(1.1);
}

.category-icon .material-symbols-outlined {
  font-size: 24px;
}

.category-card.primary .category-icon {
  background-color: rgba(142, 171, 255, 0.2);
  text-indent: -9999px;
}

.category-card.primary .category-icon .material-symbols-outlined {
  color: #8eabff;
  text-indent: -9999px;
}

.category-card.secondary .category-icon {
  background-color: rgba(188, 135, 254, 0.2);
  text-indent: -9999px;
}

.category-card.secondary .category-icon .material-symbols-outlined {
  color: #bc87fe;
  text-indent: -9999px;
}

.category-card.tertiary .category-icon {
  background-color: rgba(160, 255, 240, 0.2);
  text-indent: -9999px;
}

.category-card.tertiary .category-icon .material-symbols-outlined {
  color: #a0fff0;
  text-indent: -9999px;
}

.category-card.special {
  border: 1px solid rgba(142, 171, 255, 0.3);
}

.category-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(142, 171, 255, 0.05), rgba(188, 135, 254, 0.05));
}

.category-card.special .category-icon {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  position: relative;
  z-index: 10;
  text-indent: -9999px;
}

.category-card.special .category-icon .material-symbols-outlined {
  color: #ffffff;
  font-variation-settings: 'FILL' 1;
}

.category-name {
  font-size: 14px;
  font-weight: semibold;
  position: relative;
  z-index: 10;
}

.category-card.special .category-name {
  font-weight: bold;
}

/* 继续训练部分 */
.continue-section {
  margin-bottom: 40px;
}

.continue-card {
  position: relative;
  padding: 32px;
  border-radius: 16px;
  overflow: hidden;
}

.continue-bg-icon {
  position: absolute;
  top: 32px;
  right: 32px;
  opacity: 0.1;
}

.continue-bg-icon .material-symbols-outlined {
  font-size: 64px;
}

.continue-content {
  position: relative;
  z-index: 10;
}

.continue-badge {
  display: block;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #a0fff0;
  margin-bottom: 8px;
}

.continue-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 30px;
  font-weight: bold;
  margin-bottom: 24px;
}

.continue-progress {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 32px;
}

.progress-info {
  flex-shrink: 0;
}

.progress-percentage {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 40px;
  font-weight: bold;
  color: #8eabff;
}

.progress-unit {
  font-size: 18px;
  font-weight: normal;
  color: #adaaaa;
  margin-left: 4px;
}

.progress-label {
  font-size: 12px;
  color: #adaaaa;
  margin-top: 4px;
}

.progress-bar-container {
  flex-grow: 1;
  padding-bottom: 8px;
}

.progress-bar {
  height: 8px;
  background-color: #262626;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8eabff, #bc87fe);
  border-radius: 4px;
}

.continue-btn {
  background: linear-gradient(90deg, #8eabff, #156aff);
  color: #002971;
  font-weight: bold;
  padding: 20px 48px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 24px;
}

.continue-btn:hover {
  opacity: 0.9;
}

.continue-btn:active {
  transform: scale(0.95);
}

.continue-btn .material-symbols-outlined {
  font-size: 20px;
}

/* 课程部分 */
.courses-section {
  margin-bottom: 40px;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.section-subtitle {
  font-size: 14px;
  color: #adaaaa;
  margin-top: 4px;
}

.view-all-btn {
  background: none;
  border: none;
  color: #8eabff;
  font-size: 14px;
  font-weight: semibold;
  transition: text-decoration 0.3s ease;
}

.view-all-btn:hover {
  text-decoration: underline;
}

.courses-grid {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding-bottom: 16px;
  scroll-behavior: smooth;
}

.courses-grid::-webkit-scrollbar {
  display: none;
}

.courses-grid {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 85vw;
  max-width: 85vw;
}

.course-card:hover {
  transform: translateY(-2px);
}

.course-image-container {
  position: relative;
  aspect-ratio: 16/10;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
}

.course-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.course-card:hover .course-image {
  transform: scale(1.1);
}

.course-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent, transparent);
}

.course-meta {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-difficulty {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.course-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: bold;
  color: #ffffff;
}

.course-duration .material-symbols-outlined {
  font-size: 12px;
}

.course-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.course-description {
  font-size: 12px;
  color: #adaaaa;
}

/* 水平课程卡片 */
.course-card.horizontal {
  min-width: 85vw;
  max-width: 85vw;
  background-color: #1a1a1a;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 24px;
  transition: all 0.3s ease;
}

.course-card.horizontal:hover {
  background-color: #262626;
}

.course-image-container.horizontal {
  width: 128px;
  height: 128px;
  aspect-ratio: 1;
  flex-shrink: 0;
  margin-bottom: 0;
}

.course-content.horizontal {
  flex-grow: 1;
}

.course-badge-container {
  margin-bottom: 8px;
}

.course-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #bc87fe;
}

.course-card.horizontal .course-title {
  font-size: 20px;
  margin-bottom: 4px;
}

.course-card.horizontal .course-description {
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 12px;
}

.course-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.course-stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #adaaaa;
}

.course-stat .material-symbols-outlined {
  font-size: 14px;
}

.course-arrow {
  padding-right: 16px;
}

.arrow-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(142, 171, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8eabff;
  transition: all 0.3s ease;
}

.course-card.horizontal:hover .arrow-circle {
  background-color: #8eabff;
  color: #002971;
}

.arrow-circle .material-symbols-outlined {
  font-size: 20px;
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
  padding: 12px 20px;
  background: rgba(14, 14, 14, 0.8);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 50;
  border-radius: 32px 32px 0 0;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 20px;
  transition: all 0.3s ease;
}

.nav-item.active {
  background-color: rgba(142, 171, 255, 0.1);
  border-radius: 9999px;
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
  font-size: 11px;
  font-weight: medium;
  letter-spacing: 1px;
}

/* 玻璃面板样式 */
.glass-card {
  background: rgba(38, 38, 38, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(142, 171, 255, 0.1);
}
</style>
