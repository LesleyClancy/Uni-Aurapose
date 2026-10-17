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

      <view v-if="offlineMode" class="offline-banner">
        <text class="offline-text">{{ copy.offlineTraining }}</text>
      </view>

      <view class="mode-switch">
        <button :class="['mode-btn', { active: viewMode === 'training' }]" @click="setViewMode('training')">{{ copy.trainingMode }}</button>
        <button :class="['mode-btn', { active: viewMode === 'panorama' }]" @click="setViewMode('panorama')">{{ copy.panoramaMode }}</button>
      </view>

      <view class="preview-shell training-preview" id="previewShell">
        <!-- #ifdef MP-WEIXIN -->
        <camera
          class="camera-source"
          :device-position="cameraPosition"
          flash="off"
          @initdone="cameraInitDone"
          @error="cameraError"
        />
        <!-- #endif -->
        <!-- #ifdef APP-PLUS -->
        <live-pusher
          id="pusher"
          class="camera-source"
          mode="HD"
          :device-position="cameraPosition"
          flash="off"
          :autopush="false"
          :muted="true"
          :enable-camera="true"
          @statechange="pusherStateChange"
          @error="cameraError"
        />
        <!-- #endif -->
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
        <button class="camera-switch" @click="switchCamera">{{ copy.switchCamera }}</button>
        <view v-if="!cameraReady || modelPreparing" class="placeholder">
          <text class="placeholder-title">{{ placeholderTitle }}</text>
          <button v-if="detectorFailed" class="placeholder-retry" @click="retryDetectorInit">{{ copy.modelRetry }}</button>
        </view>
      </view>
    </view>

    <view v-else class="panorama-shell">
      <view class="preview-shell panorama-preview" id="previewShell">
        <!-- #ifdef MP-WEIXIN -->
        <camera
          class="camera-source"
          :device-position="cameraPosition"
          flash="off"
          @initdone="cameraInitDone"
          @error="cameraError"
        />
        <!-- #endif -->
        <!-- #ifdef APP-PLUS -->
        <live-pusher
          id="pusher"
          class="camera-source"
          mode="HD"
          :device-position="cameraPosition"
          flash="off"
          :autopush="false"
          :muted="true"
          :enable-camera="true"
          @statechange="pusherStateChange"
          @error="cameraError"
        />
        <!-- #endif -->
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
        <button class="camera-switch" @click="switchCamera">{{ copy.switchCamera }}</button>
        <view v-if="!cameraReady || modelPreparing" class="placeholder">
          <text class="placeholder-title">{{ placeholderTitle }}</text>
          <button v-if="detectorFailed" class="placeholder-retry" @click="retryDetectorInit">{{ copy.modelRetry }}</button>
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
          <!-- #ifdef MP-WEIXIN -->
          <view class="record-panel">
            <text class="record-title">{{ copy.panoramaRecording }}</text>
            <text class="record-subtitle">{{ isRecording ? copy.panoramaRecordingOn : copy.panoramaRecordingOff }}</text>
          </view>
          <!-- #endif -->
          <view class="panorama-actions">
            <!-- #ifdef MP-WEIXIN -->
            <button class="ghost-btn" @click="toggleRecording">
              {{ isRecording ? copy.stopRecording : copy.startRecording }}
            </button>
            <!-- #endif -->
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

    <!-- #ifdef APP-PLUS -->
    <view
      class="detector-host"
      :frame="framePayload"
      :change:frame="detector.onFrame"
      :command="commandPayload"
      :change:command="detector.onCommand"
    ></view>
    <!-- #endif -->
  </view>
</template>

<script>
import { createTrainingSession, finishTrainingSession, getApiBaseUrl, getDetectMode, getOpenid, savePendingSession } from '../../common/api.js'
import {
  applyNativeTheme,
  getThemeClass,
  getThemeMode,
  getThemeVars
} from '../../common/theme.js'
import { applyPageLocale, getCopy, getLocale } from '../../common/i18n.js'

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
      finishing: false,
      detectMode: getDetectMode(),
      cameraPosition: 'front',
      framePayload: null,
      commandPayload: null,
      frameSeq: 0,
      commandSeq: 0,
      detectorReady: false,
      detectorFailed: false,
      offlineMode: false
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
    },
    modelPreparing() {
      // #ifdef APP-PLUS
      return this.detectMode === 'local' && !this.detectorReady
      // #endif
      // #ifndef APP-PLUS
      return false
      // #endif
    },
    placeholderTitle() {
      if (this.detectorFailed) {
        return this.copy.modelLoadFailed
      }
      return this.modelPreparing ? this.copy.modelLoading : this.copy.waitingCamera
    }
  },
  onReady() {
    // #ifdef MP-WEIXIN
    this.cameraContext = uni.createCameraContext(this)
    // #endif
    // #ifdef APP-PLUS
    this.cameraContext = uni.createLivePusherContext('pusher', this)
    // #endif
    this.measurePreview()
  },
  async onShow() {
    this.syncTheme()
    this.syncLocale()
    this.detectMode = getDetectMode()
    // #ifdef APP-PLUS
    // 端侧 WASM 推理较慢，适当放慢抓帧节奏避免积压
    this.requestIntervalMs = this.detectMode === 'local' ? 100 : 50
    // #endif
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
    // #ifdef APP-PLUS
    pusherStateChange(e) {
      const detail = (e && e.detail) || {}
      // 负数 code 为 live-pusher 错误码（-1307 摄像头打开失败等）
      if (detail.code < 0) {
        this.cameraError({ detail: { errMsg: `live-pusher error code ${detail.code}` } })
        return
      }
      this.cameraInitDone()
    },
    // #endif
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
        // 离线容错：会话创建失败不阻塞训练，结束时提示未同步
        this.offlineMode = true
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
      const durationSeconds = this.startTime ? Math.floor((new Date() - this.startTime) / 1000) : 0
      let synced = false
      if (this.sessionId && durationSeconds > 0) {
        try {
          await finishTrainingSession(this.sessionId, {
            duration_seconds: durationSeconds,
            session_rpe: sessionRpe
          })
          synced = true
        } catch (err) {
          // 离线容错：同步失败转为本地存档
        }
      }
      if (!synced) {
        // 离线训练本地存档：留存训练摘要，避免数据丢失
        savePendingSession({
          finished_at: new Date().toISOString(),
          duration_seconds: durationSeconds,
          session_rpe: sessionRpe,
          total_reps: Number(this.totalReps) || 0,
          total_calories: Number(this.calories) || 0,
          counts: this.counts || {},
          calories_by_exercise: this.caloriesByExercise || {}
        })
        uni.showToast({ title: this.copy.offlineFinishNote, icon: 'none' })
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
      // #ifdef APP-PLUS
      if (this.detectMode === 'local') {
        if (!this.detectorReady) {
          if (this.isDetecting) {
            setTimeout(() => this.captureAndDetect(), 300)
          }
          return
        }
        this.sending = true
        this.cameraContext.snapshot({
          success: (res) => {
            const path = res.tempImagePath || (res.message && res.message.tempImagePath)
            if (path) {
              this.dispatchLocalFrame(path)
            } else {
              this.sending = false
              this.errorText = `${this.copy.frameCaptureFailed}: empty snapshot`
            }
          },
          fail: (err) => {
            this.sending = false
            this.errorText = `${this.copy.frameCaptureFailed}: ${(err && (err.errMsg || err.message)) || 'unknown error'}`
          }
        })
        return
      }
      // #endif
      this.sending = true
      // #ifdef MP-WEIXIN
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
      // #endif
      // #ifdef APP-PLUS
      this.cameraContext.snapshot({
        success: (res) => {
          const path = res.tempImagePath || (res.message && res.message.tempImagePath)
          if (path) {
            this.sendToBackend(path)
          } else {
            this.sending = false
            this.errorText = `${this.copy.frameCaptureFailed}: empty snapshot`
          }
        },
        fail: (err) => {
          this.sending = false
          this.errorText = `${this.copy.frameCaptureFailed}: ${(err && (err.errMsg || err.message)) || 'unknown error'}`
        }
      })
      // #endif
    },
    sendToBackend(imagePath) {
      this.readImageAsBase64(imagePath)
        .then((base64) => {
          this.postFrameToBackend(base64)
        })
        .catch((err) => {
          this.sending = false
          this.errorText = `${this.copy.imageReadFailed}: ${(err && (err.errMsg || err.message)) || err || 'unknown error'}`
        })
    },
    readImageAsBase64(imagePath) {
      // #ifdef MP-WEIXIN
      return new Promise((resolve, reject) => {
        uni.getFileSystemManager().readFile({
          filePath: imagePath,
          encoding: 'base64',
          success: (res) => resolve(res.data),
          fail: reject
        })
      })
      // #endif
      // #ifdef APP-PLUS
      return new Promise((resolve, reject) => {
        if (typeof uni.getFileSystemManager === 'function') {
          uni.getFileSystemManager().readFile({
            filePath: imagePath,
            encoding: 'base64',
            success: (res) => resolve(res.data),
            fail: reject
          })
          return
        }
        // 低版本基座无 getFileSystemManager 时，用 5+ API 读取
        plus.io.resolveLocalFileSystemURL(imagePath, (entry) => {
          entry.file((file) => {
            const reader = new plus.io.FileReader()
            reader.onload = (evt) => {
              const result = String((evt.target && evt.target.result) || '')
              resolve(result.split(',')[1] || '')
            }
            reader.onerror = (evt) => reject((evt && evt.target && evt.target.error) || new Error('read failed'))
            reader.readAsDataURL(file)
          }, reject)
        }, reject)
      })
      // #endif
    },
    postFrameToBackend(base64) {
      uni.request({
        url: `${getApiBaseUrl()}/api/realtime_frame`,
        method: 'POST',
        timeout: REQUEST_TIMEOUT,
        data: {
          openid: getOpenid(),
          session_id: this.sessionId,
          image: `data:image/jpeg;base64,${base64}`
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
    // #ifdef APP-PLUS
    dispatchLocalFrame(imagePath) {
      this.readImageAsBase64(imagePath)
        .then((base64) => {
          this.frameSeq += 1
          this.framePayload = { seq: this.frameSeq, base64 }
        })
        .catch((err) => {
          this.sending = false
          this.errorText = `${this.copy.imageReadFailed}: ${(err && (err.errMsg || err.message)) || err || 'unknown error'}`
          if (this.isDetecting) {
            setTimeout(() => this.captureAndDetect(), this.requestIntervalMs)
          }
        })
    },
    onDetectorStatus(payload) {
      if (payload && payload.ready) {
        this.detectorReady = true
        this.detectorFailed = false
        if (this.isDetecting && !this.sending) {
          this.captureAndDetect()
        }
      } else {
        this.detectorReady = false
        this.detectorFailed = true
        this.errorText = `${this.copy.modelLoadFailed}: ${(payload && payload.error) || 'unknown error'}`
      }
    },
    // #endif
    retryDetectorInit() {
      // #ifdef APP-PLUS
      this.detectorFailed = false
      this.commandSeq += 1
      this.commandPayload = { action: 'init', seq: this.commandSeq }
      // #endif
    },
    switchCamera() {
      if (!this.cameraReady) {
        return
      }
      this.cameraReady = false
      this.cameraPosition = this.cameraPosition === 'front' ? 'back' : 'front'
    },
    onDetectResult(result) {
      this.sending = false
      if (result && !result.error) {
        this.applyRealtimeResult(result)
      }
      if (this.isDetecting) {
        setTimeout(() => this.captureAndDetect(), this.requestIntervalMs)
      }
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
      // #ifdef APP-PLUS
      if (this.detectMode === 'local') {
        this.commandSeq += 1
        this.commandPayload = { action: 'reset', seq: this.commandSeq }
        this.currentExerciseKey = 'unknown'
        this.currentReps = 0
        this.totalReps = 0
        this.calories = 0
        this.counts = {}
        this.caloriesByExercise = {}
        this.landmarks = []
        return
      }
      // #endif
      uni.request({
        url: `${getApiBaseUrl()}/api/reset`,
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

<script module="detector" lang="renderjs">
// 端侧识别模块：运行在 App 视图层 WebView 中
// 加载本地 AI 资产（MediaPipe Pose + ONNX 分类器）并逐帧推理，
// 通过 $ownerInstance.callMethod 与逻辑层通信，响应结构与后端 /api/realtime_frame 同构。
import { ExerciseEngine } from '../../common/exercise-engine.js'

const CLASSIFY_INTERVAL_MS = 800

function resolveBasePath() {
  // file:// 下 location.origin 可能为 "null"，用 protocol + host 拼接更稳
  const path = window.location.pathname || '/'
  const dir = path.substring(0, path.lastIndexOf('/') + 1)
  return window.location.protocol + '//' + window.location.host + dir
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const el = document.createElement('script')
    el.src = src
    el.onload = () => resolve()
    el.onerror = () => reject(new Error('script load failed: ' + src))
    document.head.appendChild(el)
  })
}

function base64ToBytes(b64) {
  const bin = atob(b64)
  const bytes = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) {
    bytes[i] = bin.charCodeAt(i)
  }
  return bytes
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('image decode failed'))
    img.src = src
  })
}

// file:// 环境下拦截 wasm 请求，改为返回内嵌 base64 资产，保证离线可用
function patchFetchForEmbeddedAssets() {
  const originalFetch = window.fetch
  window.fetch = function patchedFetch(input, init) {
    let url = ''
    if (typeof input === 'string') {
      url = input
    } else if (input && input.url) {
      url = input.url
    }
    const name = url.split('?')[0].split('/').pop()
    const b64 = window.__AI_ASSETS && window.__AI_ASSETS[name]
    if (b64) {
      return Promise.resolve(new Response(base64ToBytes(b64), {
        status: 200,
        headers: { 'content-type': 'application/wasm' }
      }))
    }
    return originalFetch.call(window, input, init)
  }
}

export default {
  mounted() {
    this.pose = null
    this.engine = null
    this.ort = null
    this.session = null
    this.ready = false
    this.initializing = false
    this.classification = null
    this.lastClassifyAt = 0
    this.frameTimes = []
    this.init()
  },
  methods: {
    async init() {
      // 仅 App（file:// 视图层 webview）启用端侧识别；H5 页面无相机组件，跳过
      if (!/^file:/i.test(window.location.protocol)) {
        return
      }
      // 防止 mounted 与重试命令并发重复初始化
      if (this.initializing || this.ready) {
        return
      }
      this.initializing = true
      const report = (ownerInstance, payload) => {
        ownerInstance && ownerInstance.callMethod('onDetectorStatus', payload)
      }
      let owner = this.$ownerInstance
      try {
        const base = resolveBasePath()
        patchFetchForEmbeddedAssets()

        await loadScript(base + 'static/ai/embedded/ort_wasm.js')
        await loadScript(base + 'static/ai/embedded/vision_wasm.js')
        await loadScript(base + 'static/ai/embedded/pose_model.js')
        await loadScript(base + 'static/ai/embedded/onnx_model.js')
        await loadScript(base + 'static/ai/embedded/scaler.js')
        await loadScript(base + 'static/ai/vendor/ort/ort.min.js')
        await loadScript(base + 'static/ai/vendor/vision/vision_bundle.iife.js')

        const ort = window.ort
        const vision = window.MediaPipeTasksVision
        if (!ort || !vision || !window.__AI_SCALER || !window.__AI_ASSETS) {
          throw new Error('AI runtime unavailable')
        }

        ort.env.wasm.numThreads = 1
        ort.env.wasm.wasmPaths = base + 'static/ai/vendor/ort/'

        const onnxBytes = base64ToBytes(window.__AI_ASSETS['exercise_classifier.onnx'])
        const session = await ort.InferenceSession.create(onnxBytes)
        const inputName = session.inputNames[0]
        const outputName = session.outputNames[0]

        const fileset = await vision.FilesetResolver.forVisionTasks(base + 'static/ai/vendor/vision/wasm')
        const poseModelBytes = base64ToBytes(window.__AI_ASSETS['pose_landmarker_lite.task'])
        let pose
        try {
          pose = await vision.PoseLandmarker.createFromOptions(fileset, {
            baseOptions: { modelAssetBuffer: poseModelBytes, delegate: 'GPU' },
            runningMode: 'IMAGE',
            numPoses: 1
          })
        } catch (gpuError) {
          pose = await vision.PoseLandmarker.createFromOptions(fileset, {
            baseOptions: { modelAssetBuffer: poseModelBytes, delegate: 'CPU' },
            runningMode: 'IMAGE',
            numPoses: 1
          })
        }

        const scaler = window.__AI_SCALER
        const engine = new ExerciseEngine({
          scaler: { mean: scaler.mean, scale: scaler.scale },
          labels: scaler.labels,
          sequenceLength: scaler.sequence_length || 30,
          onnxRun: async (flatSequence) => {
            const tensor = new ort.Tensor('float32', flatSequence, [1, scaler.sequence_length || 30, scaler.mean.length])
            const feeds = {}
            feeds[inputName] = tensor
            const outputs = await session.run(feeds)
            return outputs[outputName].data
          }
        })

        this.ort = ort
        this.session = session
        this.pose = pose
        this.engine = engine
        this.ready = true
        // 模型已全部解码驻留，释放 base64 源字符串（约 60MB 字符串内存），降低 WebView 内存峰值
        window.__AI_ASSETS = null
        window.__AI_SCALER = null
        report(this.$ownerInstance || owner, { ready: true })
      } catch (e) {
        this.ready = false
        report(this.$ownerInstance || owner, { ready: false, error: String((e && e.message) || e) })
      } finally {
        this.initializing = false
      }
    },
    onCommand(payload) {
      if (!payload || !this.engine) {
        // 初始化失败后 engine 尚未创建，重试命令仍需放行
        if (payload && payload.action === 'init') {
          this.init()
        }
        return
      }
      if (payload.action === 'reset') {
        this.engine.reset()
        this.classification = null
        this.lastClassifyAt = 0
        this.frameTimes = []
      }
    },
    async onFrame(payload) {
      if (!payload || !payload.base64 || !this.ready || !this.pose || !this.engine) {
        return
      }
      try {
        const image = await loadImage('data:image/jpeg;base64,' + payload.base64)
        const result = this.pose.detect(image)
        const points = result && result.landmarks && result.landmarks[0]

        let flat = null
        if (points && points.length) {
          flat = new Array(132)
          for (let i = 0; i < 33; i++) {
            const p = points[i] || {}
            flat[i * 4] = p.x || 0
            flat[i * 4 + 1] = p.y || 0
            flat[i * 4 + 2] = p.z || 0
            flat[i * 4 + 3] = p.visibility != null ? p.visibility : 1
          }
        }

        let exercise = null
        let confidence = 0
        if (flat) {
          const bufferFull = this.engine.feed(flat)
          const now = Date.now()
          if (bufferFull && now - this.lastClassifyAt >= CLASSIFY_INTERVAL_MS) {
            this.lastClassifyAt = now
            const cls = await this.engine.classify()
            if (cls) {
              this.classification = cls
            }
          }
          if (this.classification) {
            exercise = this.classification.exercise
            confidence = this.classification.confidence
            this.engine.updateCounts(exercise, confidence, flat)
          }
        }

        const fps = this.trackFps()
        const response = this.engine.buildDetectResponse(exercise, confidence, flat, fps)
        this.$ownerInstance && this.$ownerInstance.callMethod('onDetectResult', response)
      } catch (e) {
        this.$ownerInstance && this.$ownerInstance.callMethod('onDetectResult', {
          error: String((e && e.message) || e)
        })
      }
    },
    trackFps() {
      const now = Date.now()
      this.frameTimes.push(now)
      while (this.frameTimes.length && now - this.frameTimes[0] > 1000) {
        this.frameTimes.shift()
      }
      return this.frameTimes.length
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  background: rgba(2, 6, 23, 0.45);
}

.placeholder-title {
  font-size: 32rpx;
  color: #ffffff;
}

.placeholder-retry {
  padding: 14rpx 36rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.35);
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-size: 26rpx;
  line-height: 1.4;
}

.camera-switch {
  position: absolute;
  left: 20rpx;
  bottom: 20rpx;
  z-index: 3;
  padding: 10rpx 20rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.28);
  border-radius: 999rpx;
  background: rgba(15, 23, 42, 0.55);
  color: #ffffff;
  font-size: 24rpx;
  line-height: 1.4;
}

.detector-host {
  position: absolute;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}

.offline-banner {
  margin-top: 16rpx;
  padding: 14rpx 20rpx;
  border-radius: 16rpx;
  background: rgba(250, 204, 21, 0.12);
  border: 1rpx solid rgba(250, 204, 21, 0.32);
}

.offline-text {
  font-size: 22rpx;
  color: #facc15;
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
