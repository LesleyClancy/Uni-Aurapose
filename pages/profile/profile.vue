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
      <!-- AI Kinetic Sphere Backdrop -->
      <div class="kinetic-sphere"></div>

      <!-- Profile Section -->
      <section class="profile-section">
        <div class="profile-avatar-container">
          <div class="profile-avatar">
            <div class="avatar-inner">
            </div>
          </div>
          <div class="profile-level">LV.1</div>
        </div>
        <h1 class="profile-name">张益达</h1>
        <p class="profile-title">健身达人 • 持续健身 128 天</p>
      </section>

      <!-- Body Data Bento Grid -->
      <section class="body-data-section">
        <h2 class="section-subtitle">身体数据</h2>
        <div class="body-data-grid">
          <div class="body-data-card">
            <p class="body-data-label">体重 (kg)</p>
            <div class="body-data-value-container">
              <span class="body-data-value">74.5</span>
              <span class="body-data-change error">-0.8</span>
            </div>
          </div>
          <div class="body-data-card">
            <p class="body-data-label">体脂率 (%)</p>
            <div class="body-data-value-container">
              <span class="body-data-value">16.2</span>
              <span class="body-data-change tertiary">-1.2%</span>
            </div>
          </div>
          <div class="body-data-card full-width">
            <div class="body-data-header">
              <p class="body-data-label">近期运动消耗 (kcal)</p>
              <text class="material-symbols-outlined trend-icon">trending_up</text>
            </div>
            <div class="body-data-chart">
              <div class="chart-bar" style="height: 40%"></div>
              <div class="chart-bar" style="height: 60%"></div>
              <div class="chart-bar primary" style="height: 85%"></div>
              <div class="chart-bar" style="height: 50%"></div>
              <div class="chart-bar secondary" style="height: 70%"></div>
              <div class="chart-bar primary active" style="height: 100%"></div>
              <div class="chart-bar" style="height: 30%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Achievements -->
      <section class="achievements-section">
        <div class="section-header">
          <h2 class="section-subtitle secondary">勋章馆</h2>
          <button class="view-all-btn">
            查看全部
          </button>
        </div>
        <div class="achievements-scroll no-scrollbar">
          <div class="achievement-item">
            <div class="achievement-icon primary">
              <text class="material-symbols-outlined">local_fire_department</text>
            </div>
            <span class="achievement-name">7天连击</span>
          </div>
          <div class="achievement-item">
            <div class="achievement-icon secondary">
              <text class="material-symbols-outlined">trophy</text>
            </div>
            <span class="achievement-name">百日精进</span>
          </div>
          <div class="achievement-item">
            <div class="achievement-icon tertiary">
              <text class="material-symbols-outlined">star</text>
            </div>
            <span class="achievement-name">早起鸟</span>
          </div>
          <div class="achievement-item locked">
            <div class="achievement-icon locked">
              <text class="material-symbols-outlined">workspace_premium</text>
            </div>
            <span class="achievement-name">深蹲大师</span>
          </div>
        </div>
      </section>

      <!-- Menu Items -->
      <section class="menu-section">
        <button class="menu-item">
          <div class="menu-item-icon primary">
            <text class="material-symbols-outlined">history</text>
          </div>
          <div class="menu-item-text-container">
            <span class="menu-item-english">history</span>
            <span class="menu-item-chinese">训练记录</span>
          </div>
        </button>
        <button class="menu-item">
          <div class="menu-item-icon secondary">
            <text class="material-symbols-outlined">favorite</text>
          </div>
          <div class="menu-item-text-container">
            <span class="menu-item-english">favorite</span>
            <span class="menu-item-chinese">我的收藏</span>
          </div>
        </button>
        <button class="menu-item">
          <div class="menu-item-icon tertiary">
            <text class="material-symbols-outlined">security</text>
          </div>
          <div class="menu-item-text-container">
            <span class="menu-item-english">security</span>
            <span class="menu-item-chinese">隐私设置</span>
          </div>
        </button>
        <button class="menu-item">
          <div class="menu-item-icon gray">
            <text class="material-symbols-outlined">help</text>
          </div>
          <div class="menu-item-text-container">
            <span class="menu-item-english">help</span>
            <span class="menu-item-chinese">帮助与反馈</span>
          </div>
        </button>
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
    // 页面方法
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
  background-color: #1a1a1a;
  transition: opacity 0.3s ease;
}

.header-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 30px;
  max-width: 7xl;
  margin: 0 auto;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 8px;
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

/* 主内容 */
.main-content {
  padding: 32px 30px;
  position: relative;
  max-width: 2xl;
  margin: 0 auto;
}

/* 动力学球体装饰 */
.kinetic-sphere {
  position: fixed;
  top: 80px;
  right: -10%;
  width: 256px;
  height: 256px;
  filter: blur(60px);
  background: radial-gradient(circle, #8eabff 0%, #bc87fe 50%, transparent 100%);
  opacity: 0.15;
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
}

/* 个人资料部分 */
.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.profile-avatar-container {
  position: relative;
  margin-bottom: 16px;
}

.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  padding: 4px;
  background: linear-gradient(to top right, #8eabff, #bc87fe, #a0fff0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #0e0e0e;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(38, 38, 38, 0.4);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(160, 255, 240, 0.3);
}

.avatar-icon {
  font-size: 40px;
  color: #a0fff0;
  font-variation-settings: 'FILL' 1;
}

.profile-level {
  position: absolute;
  bottom: 4px;
  right: -4px;
  background-color: #8eabff;
  color: #002971;
  font-size: 10px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 9999px;
  border: 2px solid #0e0e0e;
  z-index: 10;
}

.profile-name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.profile-title {
  font-size: 14px;
  color: #adaaaa;
  letter-spacing: 1px;
}

/* 身体数据部分 */
.body-data-section {
  margin-bottom: 40px;
}

.section-subtitle {
  font-size: 14px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #8eabff;
  opacity: 0.7;
  margin-bottom: 16px;
}

.section-subtitle.secondary {
  color: #bc87fe;
}

.body-data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.body-data-card {
  background-color: #20201f;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.body-data-card:hover {
  opacity: 0.9;
}

.body-data-card.full-width {
  grid-column: span 2;
}

.body-data-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  opacity: 0.2;
  transition: opacity 0.3s ease;
}

.body-data-card:hover .body-data-icon {
  opacity: 0.4;
}

.body-data-icon .material-symbols-outlined {
  font-size: 40px;
  color: #8eabff;
}

.body-data-icon.secondary .material-symbols-outlined {
  color: #bc87fe;
}

.body-data-label {
  font-size: 10px;
  color: #adaaaa;
  margin-bottom: 4px;
}

.body-data-value-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.body-data-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 30px;
  font-weight: bold;
  color: #ffffff;
}

.body-data-change {
  font-size: 12px;
  font-weight: medium;
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 4px;
}

.body-data-change.error {
  color: #ff716c;
}

.body-data-change.tertiary {
  color: #a0fff0;
}

.body-data-change .material-symbols-outlined {
  font-size: 14px;
}

.body-data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.trend-icon {
  font-size: 16px;
  color: #adaaaa;
}

.body-data-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 80px;
  gap: 8px;
}

.chart-bar {
  flex: 1;
  background-color: #262626;
  border-radius: 2px 2px 0 0;
  transition: all 0.3s ease;
}

.chart-bar.primary {
  background-color: rgba(142, 171, 255, 0.4);
}

.chart-bar.secondary {
  background-color: rgba(188, 135, 254, 0.6);
}

.chart-bar.active {
  background-color: #8eabff;
  box-shadow: 0 0 15px rgba(142, 171, 255, 0.4);
}

/* 成就部分 */
.achievements-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.view-all-btn {
  background: none;
  border: none;
  color: #adaaaa;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.3s ease;
}

.view-all-btn:hover {
  color: #bc87fe;
}

.view-all-btn .material-symbols-outlined {
  font-size: 14px;
}

.achievements-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 16px;
}

.achievement-item {
  flex-shrink: 0;
  width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.achievement-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #262626;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(142, 171, 255, 0.2);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
  text-indent: -9999px;
}

.achievement-icon .material-symbols-outlined {
  font-size: 32px;
}

.achievement-icon.primary .material-symbols-outlined {
  color: #8eabff;
  font-variation-settings: 'FILL' 1;
}

.achievement-icon.secondary .material-symbols-outlined {
  color: #bc87fe;
  font-variation-settings: 'FILL' 1;
}

.achievement-icon.tertiary .material-symbols-outlined {
  color: #a0fff0;
  font-variation-settings: 'FILL' 1;
}

.achievement-icon.locked {
  opacity: 0.3;
  border-color: rgba(72, 72, 71, 0.2);
}

.achievement-icon.locked .material-symbols-outlined {
  color: #adaaaa;
}

.achievement-item.locked {
  opacity: 0.3;
  filter: grayscale(1);
}

.achievement-name {
  font-size: 10px;
  text-align: center;
  line-height: 1.2;
  color: #ffffff;
}

/* 菜单部分 */
.menu-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 12px;
  background-color: #131313;
  transition: all 0.3s ease;
}

.menu-item:hover {
  background-color: #20201f;
}

.menu-item:active {
  transform: scale(0.98);
}

.menu-item-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.menu-item-icon .material-symbols-outlined {
  font-size: 20px;
}

.menu-item-icon.primary {
  background-color: rgba(142, 171, 255, 0.1);
}

.menu-item-icon.primary .material-symbols-outlined {
  color: #8eabff;
}

.menu-item-icon.secondary {
  background-color: rgba(188, 135, 254, 0.1);
}

.menu-item-icon.secondary .material-symbols-outlined {
  color: #bc87fe;
}

.menu-item-icon.tertiary {
  background-color: rgba(160, 255, 240, 0.1);
}

.menu-item-icon.tertiary .material-symbols-outlined {
  color: #a0fff0;
}

.menu-item-icon.gray {
  background-color: rgba(173, 170, 170, 0.1);
}

.menu-item-icon.gray .material-symbols-outlined {
  color: #adaaaa;
}

.menu-item-text-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-item-english {
  font-size: 14px;
  color: #8eabff;
  font-weight: medium;
}

.menu-item-chinese {
  font-size: 16px;
  font-weight: medium;
  color: #ffffff;
}

.menu-item-arrow {
  font-size: 20px;
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
  cursor: pointer;
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

/* 滚动条隐藏 */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
