<template>
  <view class="container bg-background">
    <!-- Top Navigation -->
    <header class="header">
      <div class="header-left">
        <span class="app-title">AuraPose</span>
      </div>
      <div class="header-right">
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content bg-mesh">
      <!-- Personalized Greeting & AI Kinetic Sphere -->
      <section class="greeting-section">
        <div class="kinetic-sphere"></div>
        <div class="greeting-content">
          <h1 class="greeting-text">你好, 健美达人</h1>
          <p class="greeting-subtext">准备好超越<br/><span class="text-primary">昨天的自己</span>了吗？</p>
          <div class="ai-suggestion glass-panel">
            <div class="ai-suggestion-content">
              <h3 class="ai-suggestion-title">AuraPose 今日建议</h3>
              <p class="ai-suggestion-text">根据你昨日的恢复数据，建议今天进行 <span class="text-secondary font-semibold">45分钟高强度间歇训练 (HIIT)</span> 以突破体能瓶颈。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Metrics Bento Grid -->
      <section class="metrics-grid">
        <!-- Calories Card -->
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon error">
              <text class="material-icons">local_fire_department</text>
            </div>
            <span class="metric-change">+12%</span>
          </div>
          <div class="metric-value">842</div>
          <div class="metric-label">千卡 (Calories)</div>
          <div class="metric-progress">
            <div class="metric-progress-bar error" style="width: 70%"></div>
          </div>
        </div>

        <!-- Minutes Card -->
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon secondary">
              <text class="material-icons">timer</text>
            </div>
            <span class="metric-change">今日目标</span>
          </div>
          <div class="metric-value">56</div>
          <div class="metric-label">分钟 (Minutes)</div>
          <div class="metric-bars">
            <div class="metric-bar tertiary" style="height: 30%"></div>
            <div class="metric-bar tertiary" style="height: 50%"></div>
            <div class="metric-bar tertiary" style="height: 80%"></div>
            <div class="metric-bar tertiary" style="height: 100%"></div>
          </div>
        </div>

        <!-- Form Score Card -->
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon primary">
              <text class="material-icons">verified</text>
            </div>
            <span class="metric-change text-primary">优秀</span>
          </div>
          <div class="metric-value">92%</div>
          <div class="metric-label">标准度 (Form Score)</div>
          <div class="metric-progress">
            <div class="metric-progress-bar primary" style="width: 92%"></div>
          </div>
        </div>

        <!-- Heart Rate Card -->
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-icon tertiary">
              <text class="material-icons">favorite</text>
            </div>
            <div class="heart-rate-bars">
              <div class="heart-rate-bar"></div>
              <div class="heart-rate-bar active"></div>
              <div class="heart-rate-bar"></div>
            </div>
          </div>
          <div class="metric-value">78</div>
          <div class="metric-label">心率 (Heart Rate)</div>
          <div class="metric-unit">bpm</div>
        </div>
      </section>

      <!-- Recommended Challenges -->
      <section class="challenges-section">
        <div class="challenges-header">
          <div class="challenges-header-left">
            <h2 class="challenges-title">个性化挑战</h2>
            <p class="challenges-subtitle">AuraPose 选出的最适合你的今日突破</p>
          </div>
          <button class="view-all-btn">
            全部挑战
          </button>
        </div>
        <div class="challenges-scroll no-scrollbar">
          <!-- Challenge Card 1 -->
          <div class="challenge-card">
            <div class="challenge-image-container">
              <img src="/static/logo.png" alt="Strength Training" class="challenge-image" />
              <div class="challenge-gradient"></div>
              <div class="challenge-content">
                <span class="challenge-badge primary">力量大师</span>
                <h3 class="challenge-title">14天硬派增肌计划</h3>
                <div class="challenge-meta">
                  <span class="challenge-meta-item">
                    45 分钟/天
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Challenge Card 2 -->
          <div class="challenge-card">
            <div class="challenge-image-container">
              <img src="/static/logo.png" alt="Yoga Session" class="challenge-image" />
              <div class="challenge-gradient"></div>
              <div class="challenge-content">
                <span class="challenge-badge tertiary">灵活性</span>
                <h3 class="challenge-title">晨间唤醒：流瑜伽</h3>
                <div class="challenge-meta">
                  <span class="challenge-meta-item">
                    20 分钟/天
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Quick AI Analysis -->
      <section class="ai-analysis glass-panel">
        <div class="ai-analysis-bg"></div>
        <div class="ai-analysis-content">
          <div class="ai-analysis-text">
            <h2 class="ai-analysis-title">AuraPose深度分析报告</h2>
            <p class="ai-analysis-description">您的肌肉群恢复率为 78%，适合进行背部与核心训练。查看完整的生物识别报告以获取更精准的训练参数。</p>
            <button class="ai-analysis-btn">查看分析详情</button>
          </div>
          <div class="ai-analysis-chart">
            <div class="chart-container">
              <svg class="chart-svg" viewBox="0 0 100 100">
                <!-- 最外层五边形 -->
                <polygon class="chart-polygon" points="50,10 85,35 75,80 25,80 15,35" />
                <!-- 第二层五边形 -->
                <polygon class="chart-polygon" points="50,20 77.5,40 67.5,70 32.5,70 22.5,40" />
                <!-- 第三层五边形 -->
                <polygon class="chart-polygon" points="50,30 70,45 60,60 40,60 30,45" />
                <!-- 第四层五边形 -->
                <polygon class="chart-polygon" points="50,40 62.5,45 55,55 45,55 37.5,45" />
                <!-- 第五层五边形 -->
                <polygon class="chart-polygon" points="50,45 57.5,47.5 52.5,52.5 47.5,52.5 42.5,47.5" />
                <!-- 中心点 -->
                <circle class="chart-center" cx="50" cy="50" r="1" />
              </svg>
              <div class="chart-label top">力量</div>
              <div class="chart-label right">爆发</div>
              <div class="chart-label bottom-right">恢复</div>
              <div class="chart-label bottom-left">柔韧</div>
              <div class="chart-label left">耐力</div>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background-color: #0e0e0e;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-btn {
  background: none;
  border: none;
  color: #adaaaa;
  font-size: 24px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(142, 171, 255, 0.2);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(142, 171, 255, 0.1);
}

.avatar-icon {
  font-size: 20px;
  color: #8eabff;
}

/* 主内容 */
.main-content {
  padding: 16px 30px;
  min-height: calc(100vh - 64px);
}

/* 背景网格 */
.bg-mesh {
  background: radial-gradient(at 0% 0%, rgba(142, 171, 255, 0.15) 0px, transparent 50%),
              radial-gradient(at 100% 100%, rgba(188, 135, 254, 0.15) 0px, transparent 50%);
}

/* 问候区域 */
.greeting-section {
  position: relative;
  padding: 32px 0;
  margin-bottom: 40px;
  overflow: hidden;
  border-radius: 24px;
}

.kinetic-sphere {
  position: absolute;
  right: -80px;
  top: -80px;
  width: 256px;
  height: 256px;
  background: linear-gradient(135deg, #8eabff 0%, #bc87fe 100%);
  filter: blur(40px);
  opacity: 0.4;
  border-radius: 50%;
}

.greeting-content {
  position: relative;
  z-index: 10;
}

.greeting-text {
  font-size: 18px;
  font-weight: medium;
  color: #adaaaa;
  margin-bottom: 4px;
}

.greeting-subtext {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 40px;
  font-weight: bold;
  line-height: 1.1;
  margin-bottom: 24px;
}

.text-primary {
  color: #8eabff;
}

.ai-suggestion {
  max-width: 400px;
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 16px;
}

.ai-suggestion-icon {
  padding: 12px;
  background-color: rgba(160, 255, 240, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-suggestion-icon .material-symbols-outlined {
  font-size: 24px;
  color: #a0fff0;
}

.ai-suggestion-title {
  font-size: 14px;
  font-weight: bold;
  color: #a0fff0;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 4px;
}

.ai-suggestion-text {
  font-size: 14px;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.9);
}

.text-secondary {
  color: #bc87fe;
}

/* 指标网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  margin-bottom: 16px;
  padding: 0 4px;
}

.metric-card {
  background-color: #1a1a1a;
  padding: 6px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  aspect-ratio: 1;
  transition: all 0.3s ease;
}

.metric-card:hover {
  background-color: #20201f;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.metric-icon {
  padding: 2px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon .material-icons {
  font-size: 10px;
}

.metric-icon.primary {
  background-color: rgba(142, 171, 255, 0.1);
}

.metric-icon.primary .material-symbols-outlined {
  color: #8eabff;
}

.metric-icon.secondary {
  background-color: rgba(188, 135, 254, 0.1);
}

.metric-icon.secondary .material-symbols-outlined {
  color: #bc87fe;
}

.metric-icon.tertiary {
  background-color: rgba(160, 255, 240, 0.1);
}

.metric-icon.tertiary .material-symbols-outlined {
  color: #a0fff0;
}

.metric-icon.error {
  background-color: rgba(255, 113, 108, 0.1);
}

.metric-icon.error .material-symbols-outlined {
  color: #ff716c;
}

.metric-change {
  font-size: 8px;
  font-weight: medium;
  color: #adaaaa;
}

.metric-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  line-height: 1;
  margin-bottom: 2px;
}

.metric-label {
  font-size: 12px;
  font-weight: medium;
  letter-spacing: 0.5px;
  color: #adaaaa;
  margin-bottom: 6px;
}

.metric-progress {
  width: 70%;
  height: 2px;
  background-color: #262626;
  border-radius: 1px;
  overflow: hidden;
  position: relative;
  margin: 0 auto;
}
.metric-progress-bar {
  height: 100%;
  border-radius: 2px;
}

.metric-progress-bar.primary {
  background-color: #8eabff;
  box-shadow: 0 0 8px rgba(142, 171, 255, 0.4);
}

.metric-progress-bar.error {
  background-color: #ff716c;
}

.metric-bars {
  display: flex;
  gap: 4px;
  height: 16px;
  align-items: flex-end;
}

.metric-bar {
  flex: 1;
  background-color: rgba(160, 255, 240, 0.2);
  border-radius: 2px 2px 0 0;
}

.metric-bar.tertiary {
  background-color: #a0fff0;
}

.heart-rate-bars {
  display: flex;
  gap: 2px;
  align-items: center;
}

.heart-rate-bar {
  width: 4px;
  border-radius: 2px;
  background-color: rgba(188, 135, 254, 0.4);
}

.heart-rate-bar:nth-child(1) {
  height: 12px;
}

.heart-rate-bar:nth-child(2) {
  height: 20px;
  background-color: #bc87fe;
}

.heart-rate-bar:nth-child(3) {
  height: 8px;
}

.metric-unit {
  font-size: 10px;
  font-weight: medium;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #bc87fe;
}

/* 挑战区域 */
.challenges-section {
  margin-bottom: 40px;
}

.challenges-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: nowrap;
}

.challenges-header-left {
  flex: 1;
  max-width: calc(100% - 100px);
}

.challenges-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.challenges-subtitle {
  font-size: 14px;
  color: #adaaaa;
}

.view-all-btn {
  background: none;
  border: none;
  color: #8eabff;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  transition: opacity 0.3s ease;
}

.view-all-btn:hover {
  opacity: 0.8;
}

.view-all-btn .material-symbols-outlined {
  font-size: 14px;
}

.challenges-scroll {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  padding-bottom: 16px;
}

.challenge-card {
  min-width: 280px;
  cursor: pointer;
}

.challenge-image-container {
  position: relative;
  aspect-ratio: 4/5;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 16px;
}

.challenge-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.7s ease;
}

.challenge-card:hover .challenge-image {
  transform: scale(1.1);
}

.challenge-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent, transparent);
}

.challenge-content {
  position: absolute;
  bottom: 24px;
  left: 24px;
  right: 24px;
}

.challenge-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.challenge-badge.primary {
  background-color: #8eabff;
  color: #002971;
}

.challenge-badge.tertiary {
  background-color: #a0fff0;
  color: #00645a;
}

.challenge-title {
  font-size: 20px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 8px;
}

.challenge-meta {
  display: flex;
  gap: 12px;
}

.challenge-meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.challenge-meta-item .material-symbols-outlined {
  font-size: 14px;
}

/* AI 分析 */
.ai-analysis {
  position: relative;
  padding: 32px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.ai-analysis-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 256px;
  height: 256px;
  background-color: rgba(188, 135, 254, 0.1);
  filter: blur(80px);
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.ai-analysis-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@media (min-width: 768px) {
  .ai-analysis-content {
    flex-direction: row;
    align-items: center;
  }
}

.ai-analysis-text {
  flex: 1;
}

.ai-analysis-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
  white-space: nowrap;
}

.ai-analysis-description {
  font-size: 16px;
  color: #adaaaa;
  margin-bottom: 24px;
}

.ai-analysis-btn {
  padding: 12px 32px;
  background: linear-gradient(90deg, #8eabff, #156aff);
  color: #002971;
  font-weight: bold;
  border-radius: 9999px;
  box-shadow: 0 4px 20px rgba(21, 106, 255, 0.3);
  transition: transform 0.3s ease;
}

.ai-analysis-btn:hover {
  transform: scale(1.05);
}

.ai-analysis-btn:active {
  transform: scale(0.95);
}

.ai-analysis-chart {
  width: 100%;
  max-width: 300px;
  aspect-ratio: 1;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 24px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.chart-polygon {
  fill: rgba(142, 171, 255, 0.1);
  stroke: rgba(142, 171, 255, 0.6);
  stroke-width: 1;
}

.chart-center {
  fill: #8eabff;
  stroke: #8eabff;
  stroke-width: 1;
}

.chart-label {
  position: absolute;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 12px;
  font-weight: bold;
  color: #adaaaa;
}

.chart-label.top {
  top: 16px;
}

.chart-label.right {
  right: 16px;
  top: 33%;
}

.chart-label.bottom-right {
  bottom: 16px;
  right: 25%;
}

.chart-label.bottom-left {
  bottom: 16px;
  left: 25%;
}

.chart-label.left {
  left: 16px;
  top: 33%;
}

/* 浮动操作按钮 */
.fab {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #8eabff, #bc87fe);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 30px rgba(188, 135, 254, 0.4);
  z-index: 40;
  transition: transform 0.3s ease;
}

.fab:hover {
  transform: scale(1.1);
}

.fab:active {
  transform: scale(0.95);
}

.fab .material-symbols-outlined {
  font-size: 32px;
  color: #002971;
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
.glass-panel {
  background: rgba(38, 38, 38, 0.4);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(142, 171, 255, 0.1);
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
