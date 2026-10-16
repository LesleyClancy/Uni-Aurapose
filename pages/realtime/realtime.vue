<template>
  <view :class="['page', themeClass, `mode-${viewMode}`]" :style="themeVars">
    <view v-if="viewMode === 'training'" class="hero">
      <view class="hero-top">
        <view class="title-group">
          <text class="eyebrow">{{ copy.eyebrow }}</text>
          <text class="title">{{ copy.title }}</text>
          <text class="subtitle">{{ copy.subtitle }}</text>
        </view>
        <view class="status-chip" :class="{ live: isDetecting }">
          <text class="status-dot"></text>
          <text class="status-text">{{ isDetecting ? copy.detecting : copy.paused }}</text>
        </view>
      </view>

      <view class="mode-switch">
        <button :class="['mode-btn', { active: viewMode === 'training' }]" @click="setViewMode('training')">{{ copy.trainingMode }}</button>
        <button :class="['mode-btn', { active: viewMode === 'panorama' }]" @click="setViewMode('panorama')">{{ copy.panoramaMode }}</button>
      </view>

      <view class="preview-shell training-preview" id="previewShell">
        <camera
          class="camera-source"
          device-position="front"
          flash="off"
          @initdone="cameraInitDone"
          @error="cameraError"
        />
        <cover-view class="skeleton-overlay">
          <cover-view
            v-for="(line, index) in skeletonLines"
            :key="`line-${index}`"
            class="skeleton-line"
            :style="line.style"
          />
          <cover-view
            v-for="(point, index) in skeletonPoints"
            :key="`point-${index}`"
            class="skeleton-point"
            :style="point.style"
          />
        </cover-view>
        <view class="preview-badge">
          <text>{{ fps }} FPS</text>
        </view>
        <view v-if="!cameraReady" class="placeholder">
          <text class="placeholder-title">{{ copy.waitingCamera }}</text>
        </view>
      </view>
    </view>

    <view v-else class="panorama-shell">
      <view class="preview-shell panorama-preview" id="previewShell">
        <camera
          class="camera-source"
          device-position="front"
          flash="off"
          @initdone="cameraInitDone"
          @error="cameraError"
        />
        <cover-view class="skeleton-overlay">
          <cover-view
            v-for="(line, index) in skeletonLines"
            :key="`p-line-${index}`"
            class="skeleton-line"
            :style="line.style"
          />
          <cover-view
            v-for="(point, index) in skeletonPoints"
            :key="`p-point-${index}`"
            class="skeleton-point"
            :style="point.style"
          />
        </cover-view>
        <view v-if="!cameraReady" class="placeholder">
          <text class="placeholder-title">{{ copy.waitingCamera }}</text>
        </view>

        <view class="panorama-overlay top">
          <view class="mode-switch overlay-switch">
            <button :class="['mode-btn', { active: viewMode === 'training' }]" @click="setViewMode('training')">{{ copy.trainingMode }}</button>
            <button :class="['mode-btn', { active: viewMode === 'panorama' }]" @click="setViewMode('panorama')">{{ copy.panoramaMode }}</button>
          </view>
          <view class="top-right-pack">
            <view class="status-chip compact" :class="{ live: isDetecting }">
              <text class="status-dot"></text>
              <text class="status-text">{{ isDetecting ? copy.detecting : copy.paused }}</text>
            </view>
            <view class="preview-badge compact-badge">
              <text>{{ fps }} FPS</text>
            </view>
          </view>
        </view>

        <view class="panorama-overlay bottom">
          <view class="record-panel">
            <text class="record-title">{{ copy.panoramaRecording }}</text>
            <text class="record-subtitle">{{ isRecording ? copy.panoramaRecordingOn : copy.panoramaRecordingOff }}</text>
          </view>
          <view class="panorama-actions">
            <button class="ghost-btn" @click="toggleRecording">
              {{ isRecording ? copy.stopRecording : copy.startRecording }}
            </button>
            <button class="danger-btn" @click="requestFinish">{{ copy.endWorkout }}</button>
          </view>
        </view>
      </view>
    </view>

    <view v-if="viewMode === 'training'" class="stats-grid">
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.currentMove }}</text>
        <text class="stat-value accent">{{ currentExerciseLabel }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.accuracy }}</text>
        <text class="stat-value">{{ accuracy }}%</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.currentReps }}</text>
        <text class="stat-value">{{ currentReps }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.totalReps }}</text>
        <text class="stat-value">{{ totalReps }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.calories }}</text>
        <text class="stat-value">{{ calories.toFixed(1) }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">{{ copy.trainingTime }}</text>
        <text class="stat-value">{{ trainingTime }}</text>
      </view>
    </view>

    <view v-if="viewMode === 'training'" class="counts-panel glass">
      <view class="panel-head">
        <text class="panel-title">{{ copy.movementSummary }}</text>
        <text class="panel-tip">{{ copy.skeletonLocal }}</text>
      </view>
      <view class="count-row" v-for="item in displayCounts" :key="item.key">
        <text class="count-name">{{ item.label }}</text>
        <text class="count-value">{{ item.count }} {{ copy.repsUnit }} / {{ item.calories.toFixed(1) }} kcal</text>
      </view>
    </view>

    <view v-if="viewMode === 'training'" class="actions">
      <button class="action-btn secondary" @click="handleReset">{{ copy.resetCounters }}</button>
      <button class="action-btn danger" @click="requestFinish">{{ copy.endWorkout }}</button>
    </view>

    <view v-if="showFinishSheet" class="finish-sheet">
      <view class="finish-backdrop" @click="cancelFinish"></view>
      <view class="finish-card glass">
        <text class="finish-title">{{ copy.finishTitle }}</text>
        <text class="finish-subtitle">{{ copy.finishSubtitle }}</text>
        <view class="finish-scale">
          <text class="finish-scale-label">{{ copy.rpeLow }}</text>
          <text class="finish-scale-label">{{ copy.rpeHigh }}</text>
        </view>
        <view class="finish-grid">
          <button
            v-for="value in rpeOptions"
            :key="value"
            class="rpe-chip"
            :disabled="finishing"
            @click="submitFinish(value)"
          >
            {{ value }}
          </button>
        </view>
        <button class="finish-cancel" :disabled="finishing" @click="cancelFinish">
          {{ finishing ? copy.finishSubmitting : copy.finishCancel }}
        </button>
      </view>
    </view>

    <text v-if="errorText" class="error-text">{{ errorText }}</text>
  </view>
</template>

<script>
import { API_BASE_URL, createTrainingSession, finishTrainingSession, getOpenid } from '../../common/api.js'
import {
  applyNativeTheme,
  getThemeClass,
  getThemeMode,
  getThemeVars
} from '../../common/theme.js'
import { applyPageLocale, getCopy, getLocale } from '../../common/i18n.js'

const SERVER_BASE_URL = API_BASE_URL
const REALTIME_API_URL = `${SERVER_BASE_URL}/api/realtime_frame`
const REQUEST_TIMEOUT = 120000

const CONNECTIONS = [
  [11, 12], [11, 23], [12, 24], [23, 24],
  [11, 13], [13, 15], [12, 14], [14, 16],
  [23, 25], [25, 27], [24, 26], [26, 28]
]

const KEYPOINTS = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

export default {
  data() {
    const locale = getLocale()
    const copy = getCopy('realtime', locale)
    return {
      themeMode: getThemeMode(),
      locale,
      viewMode: 'training',
      isDetecting: false,
      isRecording: false,
      accuracy: '0.0',
      currentExerciseKey: 'unknown',
      currentReps: 0,
      totalReps: 0,
      calories: 0,
      trainingTime: '00:00',
      fps: 0,
      counts: {},
      caloriesByExercise: {},
      cameraContext: null,
      detectionTimer: null,
      startTime: null,
      sending: false,
      cameraReady: false,
      errorText: '',
      requestIntervalMs: 50,
      previewWidth: 300,
      previewHeight: 500,
      landmarks: [],
      sessionId: null,
      lastRecordedPath: '',
      defaultNotDetected: copy.notDetected,
      showFinishSheet: false,
      finishing: false
    }
  },
  computed: {
    copy() {
      return getCopy('realtime', this.locale)
    },
    themeClass() {
      return getThemeClass(this.themeMode)
    },
    themeVars() {
      return getThemeVars(this.themeMode)
    },
    currentExerciseLabel() {
      return this.copy.exerciseMap[this.currentExerciseKey] || this.currentExerciseKey || this.copy.notDetected
    },
    displayCounts() {
      const keys = ['barbell biceps curl', 'hammer curl', 'push-up', 'shoulder press', 'squat']
      return keys.map((key) => ({
        key,
        label: this.copy.exerciseMap[key] || key,
        count: this.counts[key] || 0,
        calories: Number(this.caloriesByExercise[key] || 0)
      }))
    },
    rpeOptions() {
      return Array.from({ length: 10 }, (_, index) => index + 1)
    },
    skeletonLines() {
      return CONNECTIONS.map(([startIdx, endIdx]) => {
        const start = this.landmarks[startIdx]
        const end = this.landmarks[endIdx]
        if (!start || !end || start.visibility < 0.45 || end.visibility < 0.45) {
          return null
        }
        const startX = start.x * this.previewWidth
        const startY = start.y * this.previewHeight
        const endX = end.x * this.previewWidth
        const endY = end.y * this.previewHeight
        const deltaX = endX - startX
        const deltaY = endY - startY
        const length = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
        const angle = Math.atan2(deltaY, deltaX)
        return {
          style: `left:${startX}px;top:${startY}px;width:${length}px;transform:rotate(${angle}rad);`
        }
      }).filter(Boolean)
    },
    skeletonPoints() {
      return KEYPOINTS.map((idx) => {
        const point = this.landmarks[idx]
        if (!point || point.visibility < 0.45) {
          return null
        }
        const x = point.x * this.previewWidth - 6
        const y = point.y * this.previewHeight - 6
        return {
          style: `left:${x}px;top:${y}px;`
        }
      }).filter(Boolean)
    }
  },
  onReady() {
    this.cameraContext = uni.createCameraContext(this)
    this.measurePreview()
  },
  async onShow() {
    this.syncTheme()
    this.syncLocale()
    this.startTime = new Date()
    await this.ensureTrainingSession()
    this.startDetection()
  },
  onHide() {
    this.stopDetection()
    this.stopRecordingIfNeeded()
  },
  onUnload() {
    this.stopDetection()
    this.stopRecordingIfNeeded()
  },
  methods: {
    syncTheme() {
      this.themeMode = getThemeMode()
      applyNativeTheme(this.themeMode)
    },
    syncLocale() {
      this.locale = getLocale()
      applyPageLocale('realtime', this.locale)
    },
    setViewMode(mode) {
      this.viewMode = mode
      this.$nextTick(() => {
        this.measurePreview()
      })
    },
    measurePreview() {
      uni.createSelectorQuery()
        .in(this)
        .select('#previewShell')
        .boundingClientRect((rect) => {
          if (rect) {
            this.previewWidth = rect.width
            this.previewHeight = rect.height
          }
        })
        .exec()
    },
    cameraInitDone() {
      this.cameraReady = true
      this.errorText = ''
      this.measurePreview()
      if (this.isDetecting) {
        this.captureAndDetect()
      }
    },
    cameraError(err) {
      this.errorText = `${this.copy.cameraUnavailable}: ${(err && err.detail && err.detail.errMsg) || 'unknown error'}`
      uni.showToast({
        title: this.copy.cameraAccessFailed,
        icon: 'none'
      })
    },
    startDetection() {
      if (this.detectionTimer) {
        return
      }
      this.isDetecting = true
      this.detectionTimer = setInterval(() => {
        this.updateTrainingTime()
      }, 1000)
      this.captureAndDetect()
    },
    stopDetection() {
      this.isDetecting = false
      this.sending = false
      if (this.detectionTimer) {
        clearInterval(this.detectionTimer)
        this.detectionTimer = null
      }
    },
    async ensureTrainingSession() {
      if (this.sessionId) {
        return
      }
      try {
        const result = await createTrainingSession({})
        this.sessionId = result.session && result.session.id
      } catch (err) {
        this.errorText = `${this.copy.createSessionFailed}: ${err}`
      }
    },
    async requestFinish() {
      await this.stopRecordingIfNeeded()
      this.stopDetection()
      this.showFinishSheet = true
    },
    cancelFinish() {
      if (this.finishing) {
        return
      }
      this.showFinishSheet = false
      this.startDetection()
    },
    async submitFinish(sessionRpe) {
      if (this.finishing) {
        return
      }
      this.finishing = true
      if (this.sessionId && this.startTime) {
        const durationSeconds = Math.floor((new Date() - this.startTime) / 1000)
        try {
          await finishTrainingSession(this.sessionId, {
            duration_seconds: durationSeconds,
            session_rpe: sessionRpe
          })
        } catch (err) {
          this.errorText = `${this.copy.saveTrainingFailed}: ${err}`
          this.finishing = false
          return
        }
      }
      this.showFinishSheet = false
      this.finishing = false
      uni.navigateBack()
    },
    captureAndDetect() {
      if (!this.cameraContext || this.sending) {
        return
      }
      if (!this.cameraReady) {
        if (this.isDetecting) {
          setTimeout(() => this.captureAndDetect(), 300)
        }
        return
      }
      this.sending = true
      this.cameraContext.takePhoto({
        quality: 'low',
        success: (res) => {
          this.sendToBackend(res.tempImagePath)
        },
        fail: (err) => {
          this.sending = false
          this.errorText = `${this.copy.frameCaptureFailed}: ${err.errMsg || 'unknown error'}`
        }
      })
    },
    sendToBackend(imagePath) {
      const fileSystemManager = uni.getFileSystemManager()
      fileSystemManager.readFile({
        filePath: imagePath,
        encoding: 'base64',
        success: (res) => {
          uni.request({
            url: REALTIME_API_URL,
            method: 'POST',
            timeout: REQUEST_TIMEOUT,
            data: {
              openid: getOpenid(),
              session_id: this.sessionId,
              image: `data:image/jpeg;base64,${res.data}`
            },
            success: (response) => {
              const result = response.data || {}
              if (response.statusCode !== 200 || result.error) {
                this.errorText = `${this.copy.serverError}: ${result.error || response.statusCode}`
                return
              }
              this.applyRealtimeResult(result)
            },
            fail: (err) => {
              this.sending = false
              if (err.errMsg && err.errMsg.includes('timeout')) {
                this.errorText = this.copy.requestTimeout
              } else {
                this.errorText = `${this.copy.requestFailed}: ${err.errMsg || 'network error'}`
              }
            },
            complete: () => {
              this.sending = false
              if (this.isDetecting) {
                setTimeout(() => this.captureAndDetect(), this.requestIntervalMs)
              }
            }
          })
        },
        fail: (err) => {
          this.sending = false
          this.errorText = `${this.copy.imageReadFailed}: ${err.errMsg || 'unknown error'}`
        }
      })
    },
    applyRealtimeResult(result) {
      this.accuracy = Number(result.accuracy || 0).toFixed(1)
      this.currentExerciseKey = result.exercise || 'unknown'
      this.currentReps = Number(result.reps || 0)
      this.totalReps = Number(result.total_reps || 0)
      this.calories = Number(result.total_calories || 0)
      this.fps = Number(result.fps || 0)
      this.counts = result.counts || {}
      this.caloriesByExercise = result.calories_by_exercise || {}
      this.landmarks = result.landmarks || []
      this.errorText = ''
    },
    updateTrainingTime() {
      if (!this.startTime) {
        return
      }
      const now = new Date()
      const diff = Math.floor((now - this.startTime) / 1000)
      const minutes = String(Math.floor(diff / 60)).padStart(2, '0')
      const seconds = String(diff % 60).padStart(2, '0')
      this.trainingTime = `${minutes}:${seconds}`
    },
    handleReset() {
      uni.request({
        url: `${SERVER_BASE_URL}/api/reset`,
        method: 'POST',
        complete: () => {
          this.currentExerciseKey = 'unknown'
          this.currentReps = 0
          this.totalReps = 0
          this.calories = 0
          this.counts = {}
          this.caloriesByExercise = {}
          this.landmarks = []
        }
      })
    },
    toggleRecording() {
      if (this.isRecording) {
        this.stopRecordingIfNeeded()
        return
      }
      if (!this.cameraContext) {
        uni.showToast({ title: this.copy.cameraNotReady, icon: 'none' })
        return
      }
      this.cameraContext.startRecord({
        success: () => {
          this.isRecording = true
          uni.showToast({ title: this.copy.recordingStarted, icon: 'none' })
        },
        fail: (err) => {
          this.errorText = `${this.copy.startRecordingFailed}: ${err.errMsg || 'unknown error'}`
        }
      })
    },
    stopRecordingIfNeeded() {
      if (!this.isRecording || !this.cameraContext) {
        return Promise.resolve()
      }
      return new Promise((resolve) => {
        this.cameraContext.stopRecord({
          success: async (res) => {
            this.isRecording = false
            this.lastRecordedPath = res.tempVideoPath || ''
            if (this.lastRecordedPath) {
              await this.saveRecordedVideo(this.lastRecordedPath)
            }
            resolve()
          },
          fail: (err) => {
            this.isRecording = false
            this.errorText = `${this.copy.stopRecordingFailed}: ${err.errMsg || 'unknown error'}`
            resolve()
          }
        })
      })
    },
    saveRecordedVideo(tempVideoPath) {
      return new Promise((resolve) => {
        uni.saveVideoToPhotosAlbum({
          filePath: tempVideoPath,
          success: () => {
            uni.showToast({ title: this.copy.videoSaved, icon: 'none' })
            resolve()
          },
          fail: () => {
            uni.showModal({
              title: this.copy.saveIncompleteTitle,
              content: this.copy.saveIncompleteContent,
              showCancel: false,
              complete: () => resolve()
            })
          }
        })
      })
    }
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 28rpx 24rpx 40rpx;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top right, var(--hero-glow), transparent 28%),
    radial-gradient(circle at bottom left, rgba(255, 107, 53, 0.12), transparent 24%),
    linear-gradient(180deg, var(--page-bg) 0%, var(--page-bg-soft) 100%);
  color: var(--text);
}

.mode-panorama {
  padding: 0;
  background: #070b14;
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.title-group {
  display: flex;
  flex-direction: column;
}

.eyebrow {
  font-size: 22rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: #7dd3fc;
}

.title {
  margin-top: 8rpx;
  font-size: 48rpx;
  font-weight: 700;
}

.subtitle {
  margin-top: 12rpx;
  max-width: 520rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: var(--text-secondary);
}

.mode-switch {
  display: flex;
  gap: 12rpx;
  margin-bottom: 22rpx;
}

.overlay-switch {
  margin-bottom: 0;
}

.mode-btn {
  height: 72rpx;
  padding: 0 28rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.14);
  border: 1rpx solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.76);
  font-size: 24rpx;
}

.mode-btn.active {
  background: #ffffff;
  color: #0b1020;
}

.mode-btn::after,
.ghost-btn::after,
.danger-btn::after,
.action-btn::after {
  border: none;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 14rpx 20rpx;
  border-radius: 999rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
}

.status-chip.compact {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.16);
}

.status-chip.live {
  box-shadow: 0 0 0 1rpx rgba(34, 197, 94, 0.25), 0 0 30rpx rgba(34, 197, 94, 0.15);
}

.status-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #22c55e;
}

.status-text {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.mode-panorama .status-text {
  color: #ffffff;
}

.preview-shell {
  position: relative;
  overflow: hidden;
  background: var(--surface-strong);
  box-shadow: 0 28rpx 80rpx rgba(0, 0, 0, 0.35);
}

.training-preview {
  height: 820rpx;
  border-radius: 32rpx;
}

.panorama-preview {
  height: 100vh;
  border-radius: 0;
  box-shadow: none;
}

.camera-source,
.placeholder {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.skeleton-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
}

.skeleton-line {
  position: absolute;
  height: 4px;
  background: rgba(34, 197, 94, 0.95);
  transform-origin: left center;
  border-radius: 999px;
}

.skeleton-point {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ef4444;
  border: 2px solid #ffffff;
  box-sizing: border-box;
}

.placeholder {
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(2, 6, 23, 0.45);
}

.placeholder-title {
  font-size: 32rpx;
  color: #ffffff;
}

.preview-badge {
  position: absolute;
  right: 20rpx;
  bottom: 20rpx;
  z-index: 3;
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: var(--surface);
  color: var(--accentWarm);
  font-size: 24rpx;
}

.compact-badge {
  position: static;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.panorama-overlay {
  position: absolute;
  left: 24rpx;
  right: 24rpx;
  z-index: 4;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.panorama-overlay.top {
  top: 70rpx;
}

.panorama-overlay.bottom {
  bottom: 54rpx;
  align-items: flex-end;
  gap: 24rpx;
}

.top-right-pack {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12rpx;
}

.record-panel {
  max-width: 420rpx;
  padding: 22rpx 24rpx;
  border-radius: 28rpx;
  background: rgba(7, 11, 20, 0.56);
  backdrop-filter: blur(18rpx);
  color: #ffffff;
}

.record-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
}

.record-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 22rpx;
  line-height: 1.56;
  color: rgba(255, 255, 255, 0.82);
}

.panorama-actions {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.ghost-btn,
.danger-btn {
  min-width: 220rpx;
  height: 78rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 26rpx;
  font-size: 26rpx;
  font-weight: 700;
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.16);
  border: 1rpx solid rgba(255, 255, 255, 0.24);
  color: #ffffff;
  backdrop-filter: blur(14rpx);
}

.danger-btn {
  background: rgba(248, 113, 113, 0.88);
  color: #ffffff;
}

.stats-grid {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.glass {
  background: var(--surface);
  border: 1rpx solid var(--border);
  backdrop-filter: blur(14rpx);
}

.stat-card {
  border-radius: 24rpx;
  padding: 24rpx;
}

.stat-label {
  font-size: 24rpx;
  color: var(--text-muted);
}

.stat-value {
  margin-top: 12rpx;
  font-size: 38rpx;
  font-weight: 700;
}

.stat-value.accent {
  color: var(--brand);
}

.counts-panel {
  margin-top: 22rpx;
  border-radius: 24rpx;
  padding: 24rpx;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.panel-title {
  font-size: 30rpx;
  font-weight: 700;
}

.panel-tip {
  font-size: 22rpx;
  color: var(--text-muted);
}

.count-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid var(--border);
}

.count-row:last-child {
  border-bottom: none;
}

.count-name {
  font-size: 26rpx;
  color: var(--text);
}

.count-value {
  font-size: 24rpx;
  color: var(--brand);
}

.actions {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
}

.action-btn {
  height: 82rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.action-btn.secondary {
  background: linear-gradient(135deg, #1d4ed8 0%, #38bdf8 100%);
  color: #fff;
}

.action-btn.danger {
  background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
  color: #fff;
}

.error-text {
  display: block;
  margin-top: 22rpx;
  color: #fca5a5;
  font-size: 24rpx;
  line-height: 1.6;
  position: relative;
  z-index: 3;
}

.mode-panorama .error-text {
  position: absolute;
  left: 24rpx;
  right: 24rpx;
  bottom: 18rpx;
  margin-top: 0;
  color: #ffffff;
}

.finish-sheet {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: flex;
  align-items: flex-end;
}

.finish-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(7, 11, 20, 0.54);
}

.finish-card {
  position: relative;
  width: 100%;
  border-radius: 34rpx 34rpx 0 0;
  padding: 32rpx 28rpx 40rpx;
  background: var(--surface);
  border: 1rpx solid var(--border);
}

.finish-title,
.finish-subtitle,
.finish-scale-label {
  display: block;
}

.finish-title {
  font-size: 34rpx;
  font-weight: 700;
}

.finish-subtitle {
  margin-top: 14rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: var(--text-secondary);
}

.finish-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 24rpx;
}

.finish-scale-label {
  font-size: 22rpx;
  color: var(--text-muted);
}

.finish-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16rpx;
  margin-top: 16rpx;
}

.rpe-chip,
.finish-cancel {
  border-radius: 20rpx;
  border: 1rpx solid var(--border);
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
}

.rpe-chip::after,
.finish-cancel::after {
  border: none;
}

.rpe-chip {
  min-height: 84rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.finish-cancel {
  margin-top: 18rpx;
  min-height: 84rpx;
  font-size: 26rpx;
}
</style>
