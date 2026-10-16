<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-top"></view>
    <view class="ambient ambient-bottom"></view>

    <view class="header">
      <view>
        <text class="brand">AuraPose</text>
        <text class="header-subtitle">{{ themeMode === 'light' ? copy.dayMode : copy.nightMode }}</text>
      </view>
    </view>

    <view class="hero">
      <view class="hero-copy">
        <text class="hero-kicker">{{ heroKicker }}</text>
        <text class="hero-title">{{ copy.heroTitle }}</text>
        <text class="hero-text">{{ copy.heroText }}</text>
      </view>
      <view class="hero-note">
        <text class="hero-note-label">{{ copy.heroNoteLabel }}</text>
        <text class="hero-note-text">{{ copy.heroNoteText }}</text>
      </view>
    </view>

    <view class="focus-shell">
      <text class="focus-shell-title">{{ copy.weekTitle }}</text>
      <view class="focus-section">
        <view class="focus-card calorie-card">
          <view class="focus-head">
            <text class="focus-label">{{ copy.caloriesLabel }}</text>
            <text class="focus-trend">{{ totalCalories > 0 ? copy.caloriesTracked : '' }}</text>
          </view>
          <text class="focus-value">{{ totalCalories }}</text>
          <text class="focus-unit">kcal</text>
          <view class="energy-line">
            <view class="energy-fill" :style="{ width: calorieProgressWidth }"></view>
          </view>
          <view class="focus-foot">
            <text>{{ copy.calorieGoal }}</text>
          </view>
        </view>

        <view class="focus-card minutes-card">
          <view class="focus-head">
            <text class="focus-label">{{ copy.minutesLabel }}</text>
            <text class="focus-trend soft">{{ totalMinutes > 0 ? copy.minutesLogged : copy.minutesWaiting }}</text>
          </view>
          <view class="minutes-main">
            <view class="minutes-ring" :style="minutesRingStyle">
              <view class="minutes-ring-core">
                <text class="minutes-value">{{ totalMinutes }}</text>
                <text class="minutes-unit">{{ copy.minuteUnit }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="groups-shell">
      <view class="section-head">
        <view>
          <text class="section-kicker">{{ copy.groupsKicker }}</text>
          <text class="section-title groups-title">{{ copy.groupsTitle }}</text>
        </view>
      </view>
      <scroll-view class="groups-scroll" scroll-x="true" show-scrollbar="false">
        <view class="groups-row">
          <view v-for="item in ownedGroups" :key="item.id" :class="['group-chip-card', item.coverTheme]">
            <text class="group-chip-tag">{{ item.tag }}</text>
            <text class="group-chip-name">{{ item.name }}</text>
            <text class="group-chip-desc">{{ item.description }}</text>
            <view class="group-chip-foot">
              <text class="group-chip-meta">{{ item.members }} 人</text>
              <text class="group-chip-meta">{{ item.inviteCode }}</text>
            </view>
          </view>
          <view v-if="!ownedGroups.length" class="group-empty-card" @click="goGroups">
            <view class="group-empty-copy">
              <text class="group-empty-title">{{ copy.groupsEmptyTitle }}</text>
              <text class="group-empty-text">{{ copy.groupsEmptyText }}</text>
              <text class="group-empty-cta">{{ copy.groupsCreateCta }}</text>
            </view>
            <view class="group-empty-visual">
              <view class="group-visual-card">
                <view class="group-visual-badge">组队</view>
                <view class="team-node team-node-main">
                  <view class="team-head"></view>
                  <view class="team-body"></view>
                </view>
                <view class="team-node team-node-left">
                  <view class="team-head"></view>
                  <view class="team-body"></view>
                </view>
                <view class="team-node team-node-right">
                  <view class="team-head"></view>
                  <view class="team-body"></view>
                </view>
                <view class="team-link team-link-left"></view>
                <view class="team-link team-link-right"></view>
                <view class="team-pulse"></view>
                <view class="team-plus">+</view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="readiness-card">
      <view class="section-head readiness-head">
        <view>
          <text class="section-kicker">{{ copy.readinessKicker }}</text>
          <text class="section-title">{{ copy.readinessTitle }}</text>
        </view>
        <view class="readiness-status">
          <text class="readiness-status-label">{{ hasReadinessToday ? copy.readinessSaved : copy.readinessCta }}</text>
          <text class="readiness-status-value">{{ hasReadinessToday ? `${readinessTodayScore}/10` : '--' }}</text>
        </view>
      </view>
      <text class="readiness-text">{{ copy.readinessText }}</text>
      <view class="readiness-range">
        <text class="readiness-range-label">{{ copy.readinessScaleLow }}</text>
        <text class="readiness-range-label">{{ copy.readinessScaleHigh }}</text>
      </view>
      <view class="readiness-grid">
        <button
          v-for="value in prsOptions"
          :key="value"
          :class="['readiness-chip', { active: readinessTodayScore === value }]"
          :disabled="readinessSaving"
          @click="savePrs(value)"
        >
          {{ value }}
        </button>
      </view>
      <view class="readiness-foot">
        <text class="readiness-footline">{{ latestReadinessLabel }}</text>
        <text class="readiness-footline">{{ copy.sessionLoadTitle }}: {{ weeklySessionLoad }}</text>
      </view>
      <text class="readiness-caption">{{ copy.sessionLoadSubtitle }}</text>
    </view>

    <view class="section-head">
      <view>
        <text class="section-kicker">{{ copy.sectionKicker }}</text>
        <text class="section-title">{{ copy.sectionTitle }}</text>
      </view>
      <text class="section-link">{{ copy.sectionLink }}</text>
    </view>

    <scroll-view class="challenge-scroll" scroll-x="true" show-scrollbar="false">
      <view class="challenge-row">
        <view class="challenge-card" v-for="item in challengeCards" :key="item.title">
          <image class="challenge-image" :src="item.image" mode="aspectFill" />
          <view class="challenge-mask"></view>
          <view class="challenge-content">
            <text class="challenge-tag">{{ item.tag }}</text>
            <text class="challenge-title">{{ item.title }}</text>
            <text class="challenge-meta">{{ item.duration }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="analysis-card">
      <view class="analysis-copy">
        <text class="section-kicker">{{ copy.overviewKicker }}</text>
        <text class="analysis-title">{{ copy.overviewTitle }}</text>
        <text class="analysis-text">{{ copy.overviewText }}</text>
      </view>
      <view class="analysis-matrix">
        <view class="matrix-item" v-for="item in matrixItems" :key="item.label">
          <text class="matrix-label">{{ item.label }}</text>
          <text class="matrix-value">{{ item.value }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { fetchBootstrap, fetchProgress, fetchRecoveryStatus, saveRecoveryCheckin } from '../../common/api.js'
import {
  applyNativeTheme,
  getSceneAsset,
  getStoredProfile,
  getThemeClass,
  getThemeMode,
  getThemeVars
} from '../../common/theme.js'
import {
  applyPageLocale,
  formatMessage,
  getCopy,
  getLocale
} from '../../common/i18n.js'
import { getGroupState } from '../../common/groups.js'

const CALORIE_TARGET = 1000
const MINUTE_TARGET = 60

function percentWidth(value, max) {
  const ratio = max > 0 ? Math.min(1, Number(value || 0) / max) : 0
  return `${Math.round(ratio * 100)}%`
}

export default {
  data() {
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      bootstrap: null,
      progress: null,
      recovery: null,
      readinessSaving: false,
      groupState: getGroupState()
    }
  },
  computed: {
    copy() {
      return getCopy('home', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    displayName() {
      const user = (this.bootstrap && this.bootstrap.user) || {}
      return user.nickname || getStoredProfile().nickname || this.copy.fallbackName
    },
    heroKicker() {
      return formatMessage(this.copy.heroKicker, { name: this.displayName })
    },
    totals() {
      return ((this.bootstrap && this.bootstrap.summary) || {}).totals || {}
    },
    totalCalories() {
      return Math.round(Number(this.totals.total_calories || 0))
    },
    totalMinutes() {
      const totalSeconds = Number(this.totals.total_seconds || 0)
      return Math.floor(totalSeconds / 60)
    },
    prsOptions() {
      return Array.from({ length: 11 }, (_, index) => index)
    },
    hasReadinessToday() {
      return (((this.recovery || {}).today || {}).prs_score) !== undefined && (((this.recovery || {}).today || {}).prs_score) !== null
    },
    readinessTodayScore() {
      return Number((((this.recovery || {}).today || {}).prs_score) ?? 0) || 0
    },
    latestReadinessLabel() {
      const latest = ((this.recovery || {}).latest || {}).prs_score
      if (latest === undefined || latest === null) {
        return this.copy.readinessEmpty
      }
      return formatMessage(this.copy.readinessLatest, { score: latest })
    },
    weeklySessionLoad() {
      const overview = ((this.progress || {}).overview || {})
      return Number(overview.total_session_load || 0).toFixed(1)
    },
    calorieProgressWidth() {
      return percentWidth(this.totalCalories, CALORIE_TARGET)
    },
    minutesRingStyle() {
      const progress = percentWidth(this.totalMinutes, MINUTE_TARGET)
      return {
        background: `conic-gradient(var(--brand) 0 ${progress}, rgba(124, 228, 215, 0.18) ${progress} 100%)`
      }
    },
    matrixItems() {
      return [
        { label: this.copy.matrixMinutes, value: `${this.totalMinutes} min` },
        { label: this.copy.matrixCalories, value: `${this.totalCalories} kcal` },
        { label: this.copy.matrixSessions, value: Number(this.totals.sessions || 0) > 0 ? `${this.totals.sessions}` : '0' }
      ]
    },
    challengeCards() {
      return [
        {
          tag: this.copy.challengeStrengthTag,
          title: this.copy.challengeStrengthTitle,
          duration: this.copy.challengeStrengthDuration,
          image: getSceneAsset('strengthBuilder', this.themeMode)
        },
        {
          tag: this.copy.challengeYogaTag,
          title: this.copy.challengeYogaTitle,
          duration: this.copy.challengeYogaDuration,
          image: getSceneAsset('flowYoga', this.themeMode)
        }
      ]
    },
    ownedGroups() {
      return (this.groupState.ownedGroups || []).slice(0, 4)
    }
  },
  onLoad() {
    this.syncLocale()
    this.loadBootstrap()
    this.loadInsights()
  },
  onShow() {
    this.syncTheme()
    this.syncLocale()
    this.groupState = getGroupState()
    this.loadBootstrap()
    this.loadInsights()
  },
  methods: {
    syncTheme() {
      this.themeMode = getThemeMode()
      applyNativeTheme(this.themeMode)
    },
    syncLocale() {
      this.locale = getLocale()
      applyPageLocale('home', this.locale)
    },
    async loadBootstrap() {
      try {
        this.bootstrap = await fetchBootstrap()
      } catch (err) {
        console.warn('bootstrap failed', err)
      }
    },
    async loadInsights() {
      try {
        const [progress, recovery] = await Promise.all([
          fetchProgress(7),
          fetchRecoveryStatus()
        ])
        this.progress = progress
        this.recovery = recovery
      } catch (err) {
        console.warn('insight load failed', err)
      }
    },
    async savePrs(score) {
      if (this.readinessSaving) {
        return
      }
      this.readinessSaving = true
      try {
        this.recovery = await saveRecoveryCheckin(score)
        uni.showToast({ title: this.copy.saveSuccess, icon: 'none' })
      } catch (err) {
        uni.showToast({ title: this.copy.saveFailed, icon: 'none' })
        console.warn('save readiness failed', err)
      } finally {
        this.readinessSaving = false
      }
    },
    goGroups() {
      uni.navigateTo({ url: '/pages/groups/groups' })
    }
  },
  watch: {
    locale() {
      this.loadInsights()
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
    radial-gradient(circle at 10% 40%, var(--hero-glow-alt), transparent 26%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(70rpx);
}

.ambient-top {
  width: 260rpx;
  height: 260rpx;
  right: -90rpx;
  top: 160rpx;
  background: var(--hero-glow);
}

.ambient-bottom {
  width: 240rpx;
  height: 240rpx;
  left: -90rpx;
  bottom: 180rpx;
  background: var(--hero-glow-alt);
}

.header,
.hero,
.focus-shell,
.readiness-card,
.section-head,
.challenge-scroll,
.analysis-card {
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

.header-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-muted);
}

.hero {
  padding: 32rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-strong) 100%);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  margin-bottom: 28rpx;
}

.hero-kicker,
.section-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.hero-title {
  display: block;
  margin-top: 14rpx;
  font-size: 64rpx;
  line-height: 1.08;
  font-weight: 700;
}

.hero-text {
  display: block;
  margin-top: 18rpx;
  font-size: 26rpx;
  line-height: 1.7;
  color: var(--text-secondary);
}

.hero-note {
  margin-top: 28rpx;
  padding: 24rpx;
  border-radius: 28rpx;
  background: var(--surface-tint);
}

.hero-note-label,
.hero-note-text {
  display: block;
}

.hero-note-label {
  font-size: 22rpx;
  color: var(--brand);
  margin-bottom: 8rpx;
}

.hero-note-text {
  font-size: 26rpx;
  line-height: 1.6;
}

.focus-shell {
  margin-bottom: 34rpx;
  padding: 22rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-soft) 100%);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.groups-shell {
  position: relative;
  z-index: 2;
  margin-bottom: 30rpx;
}

.groups-title {
  font-size: 42rpx;
}

.groups-scroll {
  white-space: nowrap;
}

.groups-row {
  display: flex;
  gap: 18rpx;
  padding-right: 24rpx;
}

.group-chip-card,
.group-empty-card {
  width: 360rpx;
  min-height: 280rpx;
  padding: 26rpx;
  border-radius: 32rpx;
  flex-shrink: 0;
}

.group-chip-card {
  color: #ffffff;
  box-shadow: var(--shadow);
}

.group-empty-card {
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-strong) 100%);
  border: 1rpx dashed var(--border);
  width: calc(100vw - 60rpx);
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 176rpx;
  column-gap: 18rpx;
  align-items: start;
}

.group-chip-tag,
.group-chip-name,
.group-chip-desc,
.group-chip-meta,
.group-empty-title,
.group-empty-text,
.group-empty-cta {
  display: block;
}

.group-empty-copy {
  min-width: 0;
}

.group-chip-tag {
  display: inline-flex;
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  font-size: 20rpx;
}

.group-chip-name,
.group-empty-title {
  margin-top: 18rpx;
  font-size: 36rpx;
  font-weight: 700;
  line-height: 1.2;
}

.group-chip-desc,
.group-empty-text {
  margin-top: 12rpx;
  font-size: 22rpx;
  line-height: 1.6;
}

.group-empty-text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  max-width: 100%;
  white-space: normal;
}

.group-chip-foot {
  display: flex;
  justify-content: space-between;
  gap: 12rpx;
  margin-top: 20rpx;
}

.group-chip-meta {
  font-size: 20rpx;
  opacity: 0.92;
}

.group-empty-cta {
  margin-top: 18rpx;
  font-size: 24rpx;
  color: var(--brand);
  font-weight: 700;
}

.group-empty-visual {
  position: relative;
  width: 176rpx;
  height: 180rpx;
  align-self: end;
  justify-self: end;
}

.group-visual-card {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 176rpx;
  height: 180rpx;
  border-radius: 34rpx;
  background:
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.82) 46%, rgba(240, 246, 255, 0.64) 100%),
    linear-gradient(135deg, rgba(76, 111, 255, 0.12), rgba(45, 197, 180, 0.16));
  border: 1rpx solid rgba(115, 138, 200, 0.14);
  box-shadow:
    0 20rpx 42rpx rgba(76, 111, 255, 0.12),
    inset 0 1rpx 0 rgba(255, 255, 255, 0.9);
  overflow: hidden;
}

.group-visual-badge {
  position: absolute;
  left: 18rpx;
  top: 16rpx;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: rgba(76, 111, 255, 0.1);
  color: var(--brand);
  font-size: 18rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}

.team-node {
  position: absolute;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 8rpx solid rgba(255, 255, 255, 0.94);
  box-shadow: 0 16rpx 34rpx rgba(76, 111, 255, 0.14);
}

.team-node-main {
  width: 108rpx;
  height: 108rpx;
  left: 52rpx;
  top: 42rpx;
  background: linear-gradient(135deg, #4c6fff, #2dc5b4);
}

.team-node-left {
  width: 74rpx;
  height: 74rpx;
  left: 18rpx;
  top: 78rpx;
  background: linear-gradient(135deg, #8c7cff, #b99aff 92%);
}

.team-node-right {
  width: 78rpx;
  height: 78rpx;
  right: 16rpx;
  top: 70rpx;
  background: linear-gradient(135deg, #ff8b68, #ffb347);
}

.team-head {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.96);
}

.team-node-main .team-head {
  width: 28rpx;
  height: 28rpx;
}

.team-body {
  width: 34rpx;
  height: 22rpx;
  margin-top: 8rpx;
  border-radius: 18rpx 18rpx 12rpx 12rpx;
  background: rgba(255, 255, 255, 0.96);
}

.team-node-main .team-body {
  width: 42rpx;
  height: 26rpx;
}

.team-link {
  position: absolute;
  height: 8rpx;
  border-radius: 999rpx;
  background: linear-gradient(90deg, rgba(76, 111, 255, 0.24), rgba(45, 197, 180, 0.34));
}

.team-link-left {
  width: 54rpx;
  left: 62rpx;
  top: 106rpx;
  transform: rotate(18deg);
}

.team-link-right {
  width: 58rpx;
  right: 58rpx;
  top: 102rpx;
  transform: rotate(-18deg);
}

.team-pulse {
  position: absolute;
  left: 42rpx;
  top: 32rpx;
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  border: 2rpx dashed rgba(76, 111, 255, 0.2);
}

.team-plus {
  position: absolute;
  right: 18rpx;
  top: 18rpx;
  width: 34rpx;
  height: 34rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4c6fff, #8ca6ff);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 700;
  box-shadow: 0 10rpx 18rpx rgba(76, 111, 255, 0.18);
}

.theme-sky {
  background: linear-gradient(135deg, #4c6fff, #8ca6ff);
}

.theme-sunset {
  background: linear-gradient(135deg, #ff8b68, #ffb347);
}

.theme-mint {
  background: linear-gradient(135deg, #2dc5b4, #7ce4d7);
}

.theme-berry {
  background: linear-gradient(135deg, #8c7cff, #d87cff);
}

.focus-shell-title {
  display: block;
  margin-bottom: 18rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: var(--text-secondary);
}

.focus-section {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.focus-card {
  padding: 28rpx;
  border-radius: 32rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18rpx);
  display: flex;
  flex-direction: column;
}

.calorie-card {
  background: linear-gradient(180deg, var(--surface-strong) 0%, var(--surface) 100%);
}

.minutes-card {
  background: linear-gradient(180deg, var(--surface) 0%, var(--surface-soft) 100%);
}

.focus-head,
.focus-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.focus-label {
  font-size: 22rpx;
  color: var(--text-muted);
  letter-spacing: 3rpx;
  text-transform: uppercase;
}

.focus-trend {
  font-size: 22rpx;
  color: var(--accentWarm);
}

.focus-trend.soft {
  color: var(--brand);
}

.focus-value {
  display: block;
  margin-top: 24rpx;
  font-size: 74rpx;
  font-weight: 700;
  line-height: 1;
}

.focus-unit {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: var(--text-secondary);
}

.energy-line {
  height: 10rpx;
  margin: 30rpx 0 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 127, 92, 0.14);
  overflow: hidden;
}

.energy-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accentWarm), #ffb08b);
  box-shadow: 0 0 18rpx rgba(255, 127, 92, 0.35);
}

.focus-foot {
  font-size: 20rpx;
  color: var(--text-muted);
  margin-top: auto;
}

.minutes-main {
  margin-top: 22rpx;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.minutes-ring {
  width: 184rpx;
  height: 184rpx;
  margin: 0 auto;
  padding: 12rpx;
  border-radius: 50%;
}

.minutes-ring-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--surface-strong);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.minutes-value {
  font-size: 56rpx;
  font-weight: 700;
}

.minutes-unit {
  margin-top: 6rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 18rpx;
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

.challenge-scroll {
  margin-bottom: 28rpx;
}

.challenge-row {
  display: flex;
  gap: 20rpx;
  padding-right: 30rpx;
}

.challenge-card {
  position: relative;
  width: 520rpx;
  height: 700rpx;
  flex-shrink: 0;
  border-radius: 36rpx;
  overflow: hidden;
  box-shadow: var(--shadow);
}

.challenge-image,
.challenge-mask {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.challenge-mask {
  background: linear-gradient(180deg, transparent 25%, rgba(8, 10, 18, 0.18) 50%, rgba(8, 10, 18, 0.82) 100%);
}

.challenge-content {
  position: absolute;
  left: 28rpx;
  right: 28rpx;
  bottom: 30rpx;
  color: #ffffff;
}

.challenge-tag {
  display: inline-flex;
  margin-bottom: 14rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(16rpx);
  font-size: 22rpx;
}

.challenge-title {
  display: block;
  font-size: 44rpx;
  line-height: 1.16;
  font-weight: 700;
}

.challenge-meta {
  display: block;
  margin-top: 14rpx;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.82);
}

.analysis-card {
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.analysis-title {
  display: block;
  margin-top: 12rpx;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 1.2;
}

.analysis-text {
  display: block;
  margin-top: 16rpx;
  font-size: 26rpx;
  line-height: 1.68;
  color: var(--text-secondary);
}

.analysis-matrix {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
}

.matrix-item {
  padding: 22rpx 18rpx;
  border-radius: 24rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
}

.matrix-label,
.matrix-value {
  display: block;
}

.matrix-label {
  font-size: 20rpx;
  color: var(--text-muted);
}

.matrix-value {
  margin-top: 10rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.readiness-card {
  margin-bottom: 30rpx;
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.readiness-head {
  margin-bottom: 0;
  align-items: flex-start;
}

.readiness-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.readiness-status-label,
.readiness-status-value,
.readiness-text,
.readiness-range-label,
.readiness-footline,
.readiness-caption {
  display: block;
}

.readiness-status-label,
.readiness-caption {
  font-size: 22rpx;
  color: var(--text-muted);
}

.readiness-status-value {
  margin-top: 8rpx;
  font-size: 34rpx;
  font-weight: 700;
  color: var(--brand);
}

.readiness-text {
  margin-top: 16rpx;
  font-size: 24rpx;
  line-height: 1.66;
  color: var(--text-secondary);
}

.readiness-range {
  display: flex;
  justify-content: space-between;
  margin-top: 20rpx;
}

.readiness-range-label {
  font-size: 22rpx;
  color: var(--text-muted);
}

.readiness-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 16rpx;
}

.readiness-chip {
  min-height: 72rpx;
  border-radius: 18rpx;
  border: 1rpx solid var(--border);
  background: var(--surface-strong);
  color: var(--text);
  font-size: 24rpx;
  font-weight: 700;
}

.readiness-chip::after {
  border: none;
}

.readiness-chip.active {
  background: linear-gradient(135deg, var(--brand) 0%, var(--accentWarm) 100%);
  color: #ffffff;
}

.readiness-foot {
  display: flex;
  justify-content: space-between;
  gap: 18rpx;
  margin-top: 18rpx;
}

.readiness-footline {
  font-size: 24rpx;
  color: var(--text);
}

.readiness-caption {
  margin-top: 12rpx;
}
</style>
