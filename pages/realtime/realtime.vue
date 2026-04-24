<template>
  <view class="page">
    <view class="hero">
      <view class="hero-top">
        <view class="title-group">
          <text class="eyebrow">AI Realtime</text>
          <text class="title">动作实时识别</text>
          <text class="subtitle">后端返回动作结果和关键点，小程序本地绘制骨骼线</text>
        </view>
        <view class="status-chip" :class="{ live: isDetecting }">
          <text class="status-dot"></text>
          <text class="status-text">{{ isDetecting ? '识别中' : '已暂停' }}</text>
        </view>
      </view>

      <view class="preview-shell" id="previewShell">
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
          <text class="placeholder-title">等待摄像头初始化</text>
        </view>
      </view>
    </view>

    <view class="stats-grid">
      <view class="stat-card glass">
        <text class="stat-label">当前动作</text>
        <text class="stat-value accent">{{ currentExercise }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">识别置信度</text>
        <text class="stat-value">{{ accuracy }}%</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">当前次数</text>
        <text class="stat-value">{{ currentReps }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">总次数</text>
        <text class="stat-value">{{ totalReps }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">总卡路里</text>
        <text class="stat-value">{{ calories.toFixed(1) }}</text>
      </view>
      <view class="stat-card glass">
        <text class="stat-label">训练时长</text>
        <text class="stat-value">{{ trainingTime }}</text>
      </view>
    </view>

    <view class="counts-panel glass">
      <view class="panel-head">
        <text class="panel-title">动作统计</text>
        <text class="panel-tip">骨骼线本地绘制</text>
      </view>
      <view class="count-row" v-for="item in displayCounts" :key="item.key">
        <text class="count-name">{{ item.label }}</text>
        <text class="count-value">{{ item.count }} 次 / {{ item.calories.toFixed(1) }} 卡</text>
      </view>
    </view>

    <view class="actions">
      <button class="action-btn secondary" @click="handleReset">重置计数</button>
      <button class="action-btn danger" @click="endTraining">结束训练</button>
    </view>

    <text v-if="errorText" class="error-text">{{ errorText }}</text>
  </view>
</template>

<script>
import { API_BASE_URL, createTrainingSession, finishTrainingSession, getOpenid } from '../../common/api.js'

const SERVER_BASE_URL = API_BASE_URL
const REALTIME_API_URL = `${SERVER_BASE_URL}/api/realtime_frame`
const REQUEST_TIMEOUT = 120000

const EXERCISE_MAP = {
  'barbell biceps curl': '杠铃弯举',
  'hammer curl': '锤式弯举',
  'push-up': '俯卧撑',
  'shoulder press': '肩推',
  'squat': '深蹲',
  '未检测到': '未检测到'
}

const CONNECTIONS = [
  [11, 12], [11, 23], [12, 24], [23, 24],
  [11, 13], [13, 15], [12, 14], [14, 16],
  [23, 25], [25, 27], [24, 26], [26, 28]
]

const KEYPOINTS = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

export default {
  data() {
    return {
      isDetecting: false,
      accuracy: '0.0',
      currentExercise: '未检测到',
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
      sessionId: null
    }
  },
  computed: {
    displayCounts() {
      const keys = [
        'barbell biceps curl',
        'hammer curl',
        'push-up',
        'shoulder press',
        'squat'
      ]
      return keys.map((key) => ({
        key,
        label: EXERCISE_MAP[key] || key,
        count: this.counts[key] || 0,
        calories: Number(this.caloriesByExercise[key] || 0)
      }))
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
    this.startTime = new Date()
    await this.ensureTrainingSession()
    this.startDetection()
  },
  onHide() {
    this.stopDetection()
  },
  onUnload() {
    this.stopDetection()
  },
  methods: {
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
      this.errorText = `摄像头不可用: ${(err && err.detail && err.detail.errMsg) || 'unknown error'}`
      uni.showToast({
        title: '无法访问摄像头',
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
        this.errorText = `训练会话创建失败: ${err}`
      }
    },
    async endTraining() {
      this.stopDetection()
      if (this.sessionId && this.startTime) {
        const durationSeconds = Math.floor((new Date() - this.startTime) / 1000)
        try {
          await finishTrainingSession(this.sessionId, { duration_seconds: durationSeconds })
        } catch (err) {
          this.errorText = `训练记录保存失败: ${err}`
        }
      }
      uni.navigateBack()
    },
    captureAndDetect() {
      if (!this.cameraContext || this.sending) {
        return
      }
      if (!this.cameraReady) {
        if (this.isDetecting) {
          setTimeout(() => {
            this.captureAndDetect()
          }, 300)
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
          this.errorText = `采集画面失败: ${err.errMsg || 'unknown error'}`
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
                this.errorText = result.error || `服务异常: ${response.statusCode}`
                return
              }
              this.applyRealtimeResult(result)
            },
            fail: (err) => {
          this.sending = false
          if (err.errMsg && err.errMsg.includes('timeout')) {
            this.errorText = '请求超时，请检查网络连接或稍后重试'
          } else {
            this.errorText = `请求失败: ${err.errMsg || 'network error'}`
          }
        },
            complete: () => {
              this.sending = false
              if (this.isDetecting) {
                setTimeout(() => {
                  this.captureAndDetect()
                }, this.requestIntervalMs)
              }
            }
          })
        },
        fail: (err) => {
          this.sending = false
          this.errorText = `读取图片失败: ${err.errMsg || 'unknown error'}`
        }
      })
    },
    applyRealtimeResult(result) {
      this.accuracy = Number(result.accuracy || 0).toFixed(1)
      this.currentExercise = EXERCISE_MAP[result.exercise] || result.exercise || '未检测到'
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
          this.currentExercise = '未检测到'
          this.currentReps = 0
          this.totalReps = 0
          this.calories = 0
          this.counts = {}
          this.caloriesByExercise = {}
          this.landmarks = []
        }
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
    radial-gradient(circle at top right, rgba(46, 109, 255, 0.18), transparent 28%),
    radial-gradient(circle at bottom left, rgba(255, 107, 53, 0.14), transparent 24%),
    linear-gradient(180deg, #090f1f 0%, #0f172a 46%, #111827 100%);
  color: #f8fafc;
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
  color: #cbd5e1;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 14rpx 20rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.08);
  border: 1rpx solid rgba(255, 255, 255, 0.1);
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
  color: #e2e8f0;
}

.preview-shell {
  position: relative;
  height: 820rpx;
  border-radius: 32rpx;
  overflow: hidden;
  background: #020617;
  box-shadow: 0 28rpx 80rpx rgba(0, 0, 0, 0.35);
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
}

.preview-badge {
  position: absolute;
  right: 20rpx;
  bottom: 20rpx;
  z-index: 3;
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(15, 23, 42, 0.72);
  color: #fde68a;
  font-size: 24rpx;
}

.stats-grid {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

.glass {
  background: rgba(255, 255, 255, 0.07);
  border: 1rpx solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(14rpx);
}

.stat-card {
  border-radius: 24rpx;
  padding: 24rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #94a3b8;
}

.stat-value {
  margin-top: 12rpx;
  font-size: 38rpx;
  font-weight: 700;
}

.stat-value.accent {
  color: #7dd3fc;
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
  color: #94a3b8;
}

.count-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.06);
}

.count-row:last-child {
  border-bottom: none;
}

.count-name {
  font-size: 26rpx;
  color: #e2e8f0;
}

.count-value {
  font-size: 24rpx;
  color: #93c5fd;
}

.actions {
  margin-top: 24rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18rpx;
}

.action-btn {
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
}
</style>
