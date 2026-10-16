<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-one"></view>
    <view class="ambient ambient-two"></view>

    <view class="header">
      <text class="brand">AuraPose</text>
      <text class="header-note">{{ copy.headerNote }}</text>
    </view>

    <view class="profile-card">
      <view class="avatar-ring">
        <view class="avatar-core">
          <image v-if="profile.avatarPath" class="avatar-photo" :src="profile.avatarPath" mode="aspectFill" />
          <text v-else class="avatar-initial">{{ displayInitial }}</text>
        </view>
      </view>
      <view class="profile-copy">
        <text class="profile-name">{{ profile.nickname || copy.fallbackName }}</text>
        <text class="profile-subtitle">{{ profileSubtitle }}</text>
      </view>
      <view class="profile-pill">{{ copy.levelPrefix }}{{ level }}</view>
    </view>

    <view class="stats-grid">
      <view class="stat-card" v-for="item in stats" :key="item.label">
        <text class="stat-label">{{ item.label }}</text>
        <text class="stat-value">{{ item.value }}</text>
        <text v-if="item.foot" class="stat-foot">{{ item.foot }}</text>
      </view>
    </view>

    <view class="appearance-card">
      <view class="section-head row">
        <view>
          <text class="section-kicker">{{ progressRangeLabel }}</text>
          <text class="section-title progress-title">{{ copy.progressTitle }}</text>
        </view>
        <view class="range-toggle">
          <button
            v-for="item in progressRanges"
            :key="item.value"
            :class="['theme-option', { active: progressDays === item.value }]"
            @click="setProgressDays(item.value)"
          >
            {{ item.label }}
          </button>
        </view>
      </view>
      <view class="progress-grid">
        <view class="stat-card progress-card" v-for="item in progressStats" :key="item.label">
          <text class="stat-label">{{ item.label }}</text>
          <text class="stat-value">{{ item.value }}</text>
        </view>
      </view>
      <text class="progress-hint">{{ progressHint }}</text>
    </view>

    <view class="medal-section">
      <view class="section-head row">
        <view>
          <text class="section-kicker">{{ copy.pbKicker }}</text>
          <text class="section-title">{{ copy.pbTitle }}</text>
        </view>
      </view>
      <view class="stats-grid">
        <view class="stat-card" v-for="item in pbStats" :key="item.label">
          <text class="stat-label">{{ item.label }}</text>
          <text class="stat-value">{{ item.value }}</text>
        </view>
      </view>
      <view class="pb-exercises">
        <text class="pb-exercises-title">{{ copy.pbExercisesTitle }}</text>
        <view v-if="exercisePbs.length" class="pb-exercise-list">
          <view class="pb-exercise-item" v-for="item in exercisePbs" :key="item.exercise_key">
            <text class="pb-exercise-name">{{ exerciseLabel(item.exercise_key) }}</text>
            <text class="pb-exercise-value">{{ item.best_reps }}</text>
          </view>
        </view>
        <text v-else class="progress-hint">{{ copy.pbNoData }}</text>
      </view>
    </view>

    <view class="medal-section">
      <view class="section-head row">
        <view>
          <text class="section-kicker">{{ copy.badgesKicker }}</text>
          <text class="section-title">{{ copy.badgesTitle }}</text>
        </view>
        <text class="section-link">{{ copy.badgesLink }}</text>
      </view>
      <view class="medal-grid">
        <view class="medal-card" v-for="item in medals" :key="item.name">
          <view :class="['medal-shell', item.themeClass, { locked: item.locked }]">
            <view class="medal-halo"></view>
            <view class="medal-ribbon left"></view>
            <view class="medal-ribbon right"></view>
            <view class="medal-core">
              <text class="medal-glyph">{{ item.glyph }}</text>
            </view>
          </view>
          <text class="medal-name">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" v-for="item in menuItems" :key="item.title" @click="handleMenuClick(item)">
        <view :class="['menu-icon', item.themeClass]">
          <text class="menu-icon-glyph">{{ item.glyph }}</text>
        </view>
        <view class="menu-copy">
          <text class="menu-title">{{ item.title }}</text>
          <text class="menu-subtitle">{{ item.subtitle }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { fetchBootstrap, fetchProgress } from '../../common/api.js'
import {
  applyNativeTheme,
  getStoredProfile,
  getThemeClass,
  getThemeMode,
  getThemeVars,
  mergeStoredProfile
} from '../../common/theme.js'
import {
  applyPageLocale,
  formatMessage,
  getCopy,
  getLocale
} from '../../common/i18n.js'

function formatWeight(value) {
  return `${Number(value || 0).toFixed(1)} kg`
}

function formatHeight(value) {
  return `${Number(value || 0)} cm`
}

function formatCalories(value) {
  return `${Math.round(Number(value || 0))} kcal`
}

function formatMinutesFromSeconds(value) {
  return `${Math.floor(Number(value || 0) / 60)} min`
}

export default {
  data() {
    return {
      bootstrap: null,
      themeMode: getThemeMode(),
      locale: getLocale(),
      profile: getStoredProfile(),
      streakDays: 0,
      level: 1,
      progressDays: 7,
      progress: null
    }
  },
  computed: {
    copy() {
      return getCopy('profile', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    profileSubtitle() {
      return formatMessage(this.copy.streakText, {
        days: this.streakDays,
        mode: this.themeMode === 'light' ? this.copy.modeDay : this.copy.modeNight
      })
    },
    progressRanges() {
      return [
        { label: this.copy.progressWeek, value: 7 },
        { label: this.copy.progressMonth, value: 28 }
      ]
    },
    progressRangeLabel() {
      return this.progressDays === 28 ? this.copy.progressMonth : this.copy.progressWeek
    },
    progressOverview() {
      return (this.progress && this.progress.overview) || {}
    },
    progressStats() {
      return [
        { label: this.copy.progressActiveDays, value: `${Number(this.progressOverview.active_days || 0)}` },
        { label: this.copy.progressMinutes, value: formatMinutesFromSeconds(this.progressOverview.total_seconds) },
        { label: this.copy.progressLoad, value: Number(this.progressOverview.total_session_load || 0).toFixed(1) },
        { label: this.copy.progressReps, value: `${Number(this.progressOverview.total_reps || 0)}` }
      ]
    },
    progressHint() {
      const ratedSessions = Number(this.progressOverview.rated_sessions || 0)
      return ratedSessions > 0
        ? formatMessage(this.copy.progressRatedHint, { count: ratedSessions })
        : this.copy.progressEmptyHint
    },
    pbStats() {
      const pbs = (this.progress && this.progress.pbs) || {}
      return [
        { label: this.copy.pbReps, value: `${Number(pbs.max_total_reps || 0)}` },
        { label: this.copy.pbDuration, value: formatMinutesFromSeconds(pbs.max_duration_seconds) },
        { label: this.copy.pbCalories, value: `${Math.round(Number(pbs.max_total_calories || 0))} kcal` },
        { label: this.copy.pbLoad, value: Number(pbs.max_session_load || 0).toFixed(1) }
      ]
    },
    exercisePbs() {
      return (this.progress && this.progress.exercise_pbs) || []
    },
    medals() {
      return [
        { name: this.copy.badgeStreak, glyph: '7', themeClass: 'theme-fire', locked: false },
        { name: this.copy.badgeProgress, glyph: 'P', themeClass: 'theme-crown', locked: false },
        { name: this.copy.badgeMorning, glyph: 'A', themeClass: 'theme-mint', locked: false },
        { name: this.copy.badgeSquat, glyph: 'S', themeClass: 'theme-shadow', locked: true }
      ]
    },
    menuItems() {
      return [
        { title: this.copy.menuSettingsTitle, subtitle: this.copy.menuSettingsSubtitle, glyph: 'G', themeClass: 'theme-blue', action: 'settings' },
        { title: this.copy.menuGroupsTitle, subtitle: this.copy.menuGroupsSubtitle, glyph: 'Q', themeClass: 'theme-sunset', action: 'groups' },
        { title: this.copy.menuHistoryTitle, subtitle: this.copy.menuHistorySubtitle, glyph: 'H', themeClass: 'theme-blue' },
        { title: this.copy.menuSavedTitle, subtitle: this.copy.menuSavedSubtitle, glyph: 'S', themeClass: 'theme-purple' },
        { title: this.copy.menuPrivacyTitle, subtitle: this.copy.menuPrivacySubtitle, glyph: 'P', themeClass: 'theme-mint' },
        { title: this.copy.menuHelpTitle, subtitle: this.copy.menuHelpSubtitle, glyph: 'F', themeClass: 'theme-gray' }
      ]
    },
    stats() {
      const summary = (this.bootstrap && this.bootstrap.summary) || {}
      const latestMetric = summary.latest_metric || {}
      const totals = summary.totals || {}
      const weight = latestMetric.weight_kg ?? this.profile.weight ?? 0
      const height = this.profile.height ?? 0

      return [
        { label: this.copy.statsWeight, value: formatWeight(weight), foot: '' },
        { label: this.copy.statsHeight, value: formatHeight(height), foot: '' },
        { label: this.copy.statsCalories, value: formatCalories(totals.total_calories), foot: '' }
      ]
    },
    displayInitial() {
      const nickname = (this.profile.nickname || 'A').trim()
      return nickname.slice(0, 1).toUpperCase()
    }
  },
  onLoad() {
    this.syncLocale()
    this.loadBootstrap()
    this.loadProgress()
  },
  onShow() {
    this.syncTheme()
    this.syncLocale()
    this.profile = getStoredProfile()
    this.loadBootstrap()
    this.loadProgress()
  },
  methods: {
    syncTheme() {
      this.themeMode = getThemeMode()
      applyNativeTheme(this.themeMode)
    },
    syncLocale() {
      this.locale = getLocale()
      applyPageLocale('profile', this.locale)
    },
    setProgressDays(days) {
      this.progressDays = days
      this.loadProgress()
    },
    handleMenuClick(item) {
      if (item.action === 'settings') {
        uni.navigateTo({ url: '/pages/settings/settings' })
        return
      }
      if (item.action === 'groups') {
        uni.navigateTo({ url: '/pages/groups/groups' })
      }
    },
    exerciseLabel(key) {
      const exerciseMap = getCopy('realtime', this.locale).exerciseMap || {}
      return exerciseMap[key] || key
    },
    async loadBootstrap() {
      try {
        this.bootstrap = await fetchBootstrap()
        const user = (this.bootstrap && this.bootstrap.user) || {}
        this.streakDays = Number(user.streak_days || 0)
        this.level = Number(user.level_no || 1)
        this.profile = mergeStoredProfile({
          nickname: user.nickname || this.profile.nickname || '',
          height: user.height_cm ?? this.profile.height,
          weight: user.weight_kg ?? this.profile.weight
        })
      } catch (err) {
        console.warn('bootstrap failed', err)
      }
    },
    async loadProgress() {
      try {
        this.progress = await fetchProgress(this.progressDays)
      } catch (err) {
        console.warn('progress failed', err)
      }
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
    radial-gradient(circle at 0% 45%, var(--hero-glow-alt), transparent 26%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
  position: relative;
  overflow: hidden;
}

.ambient {
  position: absolute;
  border-radius: 999rpx;
  filter: blur(80rpx);
}

.ambient-one {
  width: 260rpx;
  height: 260rpx;
  right: -110rpx;
  top: 180rpx;
  background: var(--hero-glow);
}

.ambient-two {
  width: 240rpx;
  height: 240rpx;
  left: -100rpx;
  bottom: 240rpx;
  background: var(--hero-glow-alt);
}

.header,
.profile-card,
.appearance-card,
.stats-grid,
.medal-section,
.menu-list {
  position: relative;
  z-index: 2;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 26rpx;
}

.brand {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--brand);
}

.header-note {
  font-size: 24rpx;
  color: var(--text-muted);
}

.profile-card,
.appearance-card,
.medal-section {
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  backdrop-filter: blur(18rpx);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 22rpx;
  margin-bottom: 22rpx;
}

.appearance-card {
  margin-bottom: 22rpx;
}

.avatar-ring {
  width: 132rpx;
  height: 132rpx;
  padding: 6rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  flex-shrink: 0;
}

.avatar-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--surface-strong);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.avatar-initial {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--brand);
}

.profile-copy {
  flex: 1;
  min-width: 0;
}

.profile-name,
.profile-subtitle {
  display: block;
}

.profile-name {
  font-size: 42rpx;
  font-weight: 700;
}

.profile-subtitle {
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: var(--text-secondary);
}

.profile-pill {
  padding: 12rpx 20rpx;
  border-radius: 999rpx;
  background: var(--surface-tint);
  color: var(--brand);
  font-size: 22rpx;
  flex-shrink: 0;
}

.section-head {
  margin-bottom: 18rpx;
}

.section-head.row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.section-kicker {
  display: block;
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: var(--text-muted);
}

.section-title {
  display: block;
  margin-top: 10rpx;
  font-size: 42rpx;
  line-height: 1.18;
  font-weight: 700;
}

.section-link {
  font-size: 24rpx;
  color: var(--brand);
}

.theme-option {
  height: 88rpx;
  border-radius: 24rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
  color: var(--text-secondary);
  font-size: 28rpx;
}

.theme-option.active {
  background: linear-gradient(135deg, var(--brand), var(--brand-soft));
  color: #ffffff;
  box-shadow: 0 18rpx 36rpx rgba(76, 111, 255, 0.24);
}

.theme-option::after {
  border: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14rpx;
  margin-bottom: 22rpx;
}

.stat-card {
  padding: 24rpx 18rpx;
  border-radius: 28rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.stat-label,
.stat-value,
.stat-foot {
  display: block;
}

.stat-label {
  font-size: 22rpx;
  color: var(--text-muted);
}

.stat-value {
  margin-top: 14rpx;
  font-size: 34rpx;
  font-weight: 700;
}

.stat-foot {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
  line-height: 1.5;
  min-height: 0;
}

.medal-section {
  margin-bottom: 22rpx;
}

.progress-title {
  font-size: 38rpx;
}

.range-toggle {
  display: flex;
  gap: 12rpx;
}

.range-toggle .theme-option {
  min-width: 132rpx;
  height: 72rpx;
  padding: 0 20rpx;
  border-radius: 18rpx;
  font-size: 24rpx;
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14rpx;
}

.progress-card {
  box-shadow: none;
  background: var(--surface-strong);
}

.progress-hint,
.pb-exercises-title,
.pb-exercise-name,
.pb-exercise-value {
  display: block;
}

.progress-hint {
  margin-top: 16rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: var(--text-secondary);
}

.pb-exercises {
  margin-top: 18rpx;
}

.pb-exercises-title {
  font-size: 24rpx;
  font-weight: 700;
  color: var(--text-secondary);
}

.pb-exercise-list {
  margin-top: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.pb-exercise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 18rpx;
  border-radius: 22rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
}

.pb-exercise-name {
  font-size: 24rpx;
  color: var(--text);
}

.pb-exercise-value {
  font-size: 26rpx;
  font-weight: 700;
  color: var(--brand);
}

.medal-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16rpx;
}

.medal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.medal-shell {
  position: relative;
  width: 132rpx;
  height: 148rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.medal-halo {
  position: absolute;
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  opacity: 0.24;
}

.medal-ribbon {
  position: absolute;
  bottom: 8rpx;
  width: 24rpx;
  height: 36rpx;
  border-radius: 0 0 10rpx 10rpx;
}

.medal-ribbon.left {
  left: 34rpx;
}

.medal-ribbon.right {
  right: 34rpx;
}

.medal-core {
  position: relative;
  z-index: 2;
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 6rpx solid rgba(255, 255, 255, 0.26);
  box-shadow: inset 0 0 0 1rpx rgba(255, 255, 255, 0.22);
}

.medal-glyph {
  font-size: 34rpx;
  font-weight: 700;
  color: #ffffff;
}

.medal-name {
  margin-top: 10rpx;
  font-size: 22rpx;
  text-align: center;
}

.theme-fire .medal-halo,
.theme-fire .medal-core,
.theme-fire .medal-ribbon {
  background: linear-gradient(135deg, #ff8c66, #ff5b45);
}

.theme-crown .medal-halo,
.theme-crown .medal-core,
.theme-crown .medal-ribbon {
  background: linear-gradient(135deg, #8679ff, #b79cff);
}

.theme-mint .medal-halo,
.theme-mint .medal-core,
.theme-mint .medal-ribbon {
  background: linear-gradient(135deg, #43d6bf, #7ce4d7);
}

.theme-shadow .medal-halo,
.theme-shadow .medal-core,
.theme-shadow .medal-ribbon {
  background: linear-gradient(135deg, #7f8aa6, #a3adc2);
}

.locked {
  filter: grayscale(1);
  opacity: 0.45;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 22rpx;
  border-radius: 28rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.menu-icon {
  width: 76rpx;
  height: 76rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon-glyph {
  font-size: 30rpx;
  font-weight: 700;
  color: #ffffff;
}

.menu-copy {
  flex: 1;
  min-width: 0;
}

.menu-title,
.menu-subtitle {
  display: block;
}

.menu-title {
  font-size: 30rpx;
  font-weight: 700;
}

.menu-subtitle {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
  line-height: 1.5;
}

.theme-blue {
  background: linear-gradient(135deg, #4c6fff, #8ca6ff);
}

.theme-purple {
  background: linear-gradient(135deg, #8c7cff, #be9cff);
}

.theme-sunset {
  background: linear-gradient(135deg, #ff8b68, #ffb347);
}

.theme-mint {
  background: linear-gradient(135deg, #2dc5b4, #7ce4d7);
}

.theme-gray {
  background: linear-gradient(135deg, #8591a4, #abb5c6);
}
</style>
