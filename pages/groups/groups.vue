<template>
  <view :class="['page', themeClass]" :style="themeVars">
    <view class="ambient ambient-left"></view>
    <view class="ambient ambient-right"></view>

    <view class="hero">
      <view class="hero-copy">
        <text class="hero-kicker">{{ copy.heroKicker }}</text>
        <text class="hero-title">{{ copy.heroTitle }}</text>
        <text class="hero-subtitle">{{ copy.heroSubtitle }}</text>
      </view>
      <view class="hero-cluster">
        <view class="cluster cluster-large">A</view>
        <view class="cluster cluster-left">R</view>
        <view class="cluster cluster-right">P</view>
      </view>
    </view>

    <view class="action-grid">
      <view class="action-card action-create" @click="openCreatePanel">
        <view>
          <text class="action-title">{{ copy.createTitle }}</text>
          <text class="action-subtitle">{{ copy.createSubtitle }}</text>
        </view>
        <text class="action-glyph">+</text>
      </view>
      <view class="action-card action-join" @click="openJoinPanel">
        <view>
          <text class="action-title">{{ copy.joinTitle }}</text>
          <text class="action-subtitle">{{ copy.joinSubtitle }}</text>
        </view>
        <text class="action-glyph">∞</text>
      </view>
    </view>

    <view class="section-card">
      <view class="section-head">
        <view>
          <text class="section-kicker">{{ copy.ownedKicker }}</text>
          <text class="section-title">{{ copy.ownedTitle }}</text>
        </view>
        <text class="section-link" @click="openCreatePanel">{{ copy.createCta }}</text>
      </view>
      <scroll-view class="owned-scroll" scroll-x="true" show-scrollbar="false">
        <view class="owned-row">
          <view v-for="item in ownedGroups" :key="item.id" :class="['owned-card', item.coverTheme]">
            <text class="owned-badge">{{ item.tag }}</text>
            <text class="owned-title">{{ item.name }}</text>
            <text class="owned-desc">{{ item.description }}</text>
            <view class="owned-foot">
              <text class="owned-meta">{{ item.members }} {{ copy.membersUnit }}</text>
              <text class="owned-meta">{{ copy.inviteCodeLabel }} {{ item.inviteCode }}</text>
            </view>
          </view>
          <view v-if="!ownedGroups.length" class="owned-empty">
            <text class="owned-empty-title">{{ copy.emptyOwnedTitle }}</text>
            <text class="owned-empty-text">{{ copy.emptyOwnedText }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <view v-if="popularGroups.length" class="section-card">
      <view class="section-head">
        <view>
          <text class="section-kicker">{{ copy.popularKicker }}</text>
          <text class="section-title">{{ copy.popularTitle }}</text>
        </view>
      </view>
      <view class="popular-grid">
        <view v-for="item in popularGroups" :key="item.id" class="popular-card">
          <view class="popular-cover" :class="item.coverTheme">
            <view class="popular-tag">{{ item.tag }}</view>
            <view class="popular-avatar">{{ item.name.slice(0, 1) }}</view>
          </view>
          <view class="popular-copy">
            <text class="popular-name">{{ item.name }}</text>
            <text class="popular-desc">{{ item.description }}</text>
            <view class="popular-foot">
              <text class="popular-meta">{{ item.members }} {{ copy.joinedUnit }}</text>
              <button class="popular-btn" @click.stop="quickJoin(item)">
                {{ isJoined(item.id) ? copy.joinedLabel : copy.joinLabel }}
              </button>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="panelMode" class="panel-mask" @click="closePanel">
      <view class="panel-sheet" @click.stop>
        <text class="panel-title">{{ panelMode === 'create' ? copy.createPanelTitle : copy.joinPanelTitle }}</text>
        <text class="panel-subtitle">{{ panelMode === 'create' ? copy.createPanelSubtitle : copy.joinPanelSubtitle }}</text>

        <input
          v-model.trim="draftName"
          class="panel-input"
          :placeholder="panelMode === 'create' ? copy.groupNamePlaceholder : copy.inviteCodePlaceholder"
          :placeholder-style="placeholderStyle"
        />

        <input
          v-if="panelMode === 'create'"
          v-model.trim="draftDescription"
          class="panel-input"
          :placeholder="copy.groupDescPlaceholder"
          :placeholder-style="placeholderStyle"
        />

        <view v-if="panelMode === 'create'" class="theme-picks">
          <view
            v-for="item in themeChoices"
            :key="item.value"
            :class="['theme-dot', item.value, { active: draftTheme === item.value }]"
            @click="draftTheme = item.value"
          ></view>
        </view>

        <view class="panel-actions">
          <button class="ghost-btn" @click="closePanel">{{ copy.cancelLabel }}</button>
          <button class="confirm-btn" @click="submitPanel">{{ panelMode === 'create' ? copy.createConfirm : copy.joinConfirm }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import {
  applyNativeTheme,
  getThemeClass,
  getThemeMode,
  getThemeVars
} from '../../common/theme.js'
import {
  applyPageLocale,
  getCopy,
  getLocale
} from '../../common/i18n.js'
import {
  createLocalGroup,
  getGroupState,
  joinLocalGroup
} from '../../common/groups.js'

export default {
  data() {
    return {
      themeMode: getThemeMode(),
      locale: getLocale(),
      groupState: getGroupState(),
      panelMode: '',
      draftName: '',
      draftDescription: '',
      draftTheme: 'theme-sky'
    }
  },
  computed: {
    copy() {
      return getCopy('groups', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    placeholderStyle() {
      return `color:${this.themeMode === 'light' ? '#9aa5b5' : '#66738f'}`
    },
    ownedGroups() {
      return this.groupState.ownedGroups || []
    },
    popularGroups() {
      return this.groupState.popularGroups || []
    },
    themeChoices() {
      return [
        { value: 'theme-sky' },
        { value: 'theme-sunset' },
        { value: 'theme-mint' },
        { value: 'theme-berry' }
      ]
    }
  },
  onLoad() {
    this.syncPageState()
  },
  onShow() {
    this.syncPageState()
    this.groupState = getGroupState()
  },
  methods: {
    syncPageState() {
      this.themeMode = getThemeMode()
      this.locale = getLocale()
      applyNativeTheme(this.themeMode)
      applyPageLocale('groups', this.locale)
    },
    isJoined(groupId) {
      return (this.groupState.joinedGroupIds || []).includes(groupId)
    },
    openCreatePanel() {
      this.panelMode = 'create'
      this.draftName = ''
      this.draftDescription = ''
      this.draftTheme = 'theme-sky'
    },
    openJoinPanel() {
      this.panelMode = 'join'
      this.draftName = ''
      this.draftDescription = ''
    },
    closePanel() {
      this.panelMode = ''
    },
    submitPanel() {
      if (this.panelMode === 'create') {
        createLocalGroup({
          name: this.draftName || this.copy.defaultGroupName,
          tag: this.copy.defaultTag,
          description: this.draftDescription || this.copy.defaultGroupDesc,
          coverTheme: this.draftTheme
        })
        uni.showToast({ title: this.copy.createSuccess, icon: 'none' })
      } else if (this.popularGroups.length) {
        joinLocalGroup(this.popularGroups[0].id)
        uni.showToast({ title: this.copy.joinSuccess, icon: 'none' })
      }
      this.groupState = getGroupState()
      this.closePanel()
    },
    quickJoin(item) {
      if (this.isJoined(item.id)) {
        return
      }
      joinLocalGroup(item.id)
      this.groupState = getGroupState()
      uni.showToast({ title: this.copy.joinSuccess, icon: 'none' })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 36rpx 30rpx 56rpx;
  background:
    radial-gradient(circle at top left, var(--hero-glow-alt), transparent 28%),
    radial-gradient(circle at top right, var(--hero-glow), transparent 34%),
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

.ambient-left {
  width: 260rpx;
  height: 260rpx;
  left: -80rpx;
  top: 220rpx;
  background: var(--hero-glow-alt);
}

.ambient-right {
  width: 280rpx;
  height: 280rpx;
  right: -120rpx;
  top: 140rpx;
  background: var(--hero-glow);
}

.hero,
.action-grid,
.section-card {
  position: relative;
  z-index: 2;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 26rpx;
  padding: 30rpx;
  border-radius: 36rpx;
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-strong) 100%);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
}

.hero-copy {
  flex: 1;
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
  font-size: 60rpx;
  line-height: 1.08;
  font-weight: 700;
}

.hero-subtitle {
  display: block;
  margin-top: 16rpx;
  font-size: 24rpx;
  line-height: 1.65;
  color: var(--text-secondary);
}

.hero-cluster {
  position: relative;
  width: 220rpx;
  height: 180rpx;
  flex-shrink: 0;
}

.cluster {
  position: absolute;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 700;
  border: 8rpx solid rgba(255, 255, 255, 0.92);
  box-shadow: 0 16rpx 36rpx rgba(18, 32, 51, 0.16);
}

.cluster-large {
  width: 120rpx;
  height: 120rpx;
  left: 50rpx;
  top: 42rpx;
  background: linear-gradient(135deg, #4c6fff, #2dc5b4);
  font-size: 42rpx;
}

.cluster-left {
  width: 88rpx;
  height: 88rpx;
  left: 0;
  top: 22rpx;
  background: linear-gradient(135deg, #7f8dff, #b59bff);
  font-size: 30rpx;
}

.cluster-right {
  width: 92rpx;
  height: 92rpx;
  right: 0;
  top: 10rpx;
  background: linear-gradient(135deg, #ff8b68, #ffb347);
  font-size: 30rpx;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.action-card {
  padding: 28rpx;
  border-radius: 32rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-create {
  background: linear-gradient(135deg, rgba(76, 111, 255, 0.16), var(--surface));
}

.action-join {
  background: linear-gradient(135deg, rgba(255, 144, 105, 0.16), var(--surface));
}

.action-title,
.action-subtitle {
  display: block;
}

.action-title {
  font-size: 34rpx;
  font-weight: 700;
}

.action-subtitle {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-secondary);
}

.action-glyph {
  font-size: 48rpx;
  color: var(--brand);
}

.section-card {
  margin-bottom: 24rpx;
  padding: 30rpx;
  border-radius: 34rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  box-shadow: var(--shadow);
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
  font-size: 42rpx;
  font-weight: 700;
}

.section-link {
  font-size: 24rpx;
  color: var(--brand);
}

.owned-scroll {
  white-space: nowrap;
}

.owned-row {
  display: flex;
  gap: 18rpx;
  padding-right: 20rpx;
}

.owned-card,
.owned-empty {
  width: 420rpx;
  min-height: 240rpx;
  padding: 28rpx;
  border-radius: 32rpx;
  color: #ffffff;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.owned-empty {
  background: linear-gradient(135deg, var(--surface-soft), var(--surface-strong));
  color: var(--text);
  border: 1rpx dashed var(--border);
}

.owned-badge,
.owned-title,
.owned-desc,
.owned-meta,
.owned-empty-title,
.owned-empty-text {
  display: block;
}

.owned-badge {
  align-self: flex-start;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  font-size: 20rpx;
}

.owned-title,
.owned-empty-title {
  margin-top: 20rpx;
  font-size: 40rpx;
  font-weight: 700;
}

.owned-desc,
.owned-empty-text {
  margin-top: 14rpx;
  font-size: 22rpx;
  line-height: 1.6;
}

.owned-foot {
  display: flex;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 22rpx;
}

.owned-meta {
  font-size: 20rpx;
  opacity: 0.9;
}

.popular-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.popular-card {
  overflow: hidden;
  border-radius: 30rpx;
  background: var(--surface-strong);
  border: 1rpx solid var(--border);
}

.popular-cover {
  position: relative;
  height: 180rpx;
  padding: 18rpx;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.popular-tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 20rpx;
}

.popular-avatar {
  width: 74rpx;
  height: 74rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
  color: var(--text);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
}

.popular-copy {
  padding: 20rpx 20rpx 22rpx;
}

.popular-name,
.popular-desc,
.popular-meta {
  display: block;
}

.popular-name {
  font-size: 32rpx;
  font-weight: 700;
}

.popular-desc {
  margin-top: 10rpx;
  min-height: 70rpx;
  font-size: 22rpx;
  line-height: 1.55;
  color: var(--text-secondary);
}

.popular-foot {
  margin-top: 18rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popular-meta {
  font-size: 22rpx;
  color: var(--text-muted);
}

.popular-btn {
  min-width: 136rpx;
  height: 66rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ff8b34, #ff6a00);
  color: #ffffff;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.popular-btn::after {
  border: none;
}

.panel-mask {
  position: fixed;
  inset: 0;
  z-index: 9;
  background: rgba(8, 14, 24, 0.32);
  display: flex;
  align-items: flex-end;
}

.panel-sheet {
  width: 100%;
  padding: 32rpx 30rpx 40rpx;
  border-radius: 36rpx 36rpx 0 0;
  background: var(--surface-strong);
  box-shadow: 0 -16rpx 60rpx rgba(18, 32, 51, 0.12);
}

.panel-title,
.panel-subtitle {
  display: block;
}

.panel-title {
  font-size: 42rpx;
  font-weight: 700;
}

.panel-subtitle {
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--text-secondary);
}

.panel-input {
  width: 100%;
  height: 92rpx;
  margin-top: 18rpx;
  padding: 0 26rpx;
  border-radius: 24rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
  color: var(--text);
  font-size: 28rpx;
  box-sizing: border-box;
}

.theme-picks {
  display: flex;
  gap: 16rpx;
  margin-top: 22rpx;
}

.theme-dot {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  border: 4rpx solid transparent;
}

.theme-dot.active {
  border-color: var(--text);
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

.panel-actions {
  display: flex;
  gap: 14rpx;
  margin-top: 28rpx;
}

.ghost-btn,
.confirm-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 28rpx;
  font-weight: 700;
}

.ghost-btn {
  background: var(--surface);
  border: 1rpx solid var(--border);
  color: var(--text);
}

.confirm-btn {
  background: linear-gradient(135deg, var(--brand), var(--brand-soft));
  color: #ffffff;
}

.ghost-btn::after,
.confirm-btn::after {
  border: none;
}
</style>
