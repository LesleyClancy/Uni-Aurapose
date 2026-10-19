/**
 * 端侧健身动作识别引擎（纯算法，无 uni/DOM 依赖）
 * 忠实移植自 python_backend/old.py 的 ExerciseRecognitionSystemPC：
 *  - 特征工程 extract_advanced_features_from_landmarks (L491-678)
 *  - 分类流程 predict_exercise (L1546-1591)
 *  - 计数状态机 ExerciseCounterOptimized (L681-1320)
 *  - 卡路里 CalorieCalculator (L73-162)
 *  - 响应结构 build_detect_response/serialize_landmarks (server.py L919-962)
 * 阈值与状态转移逐行对照移植，请勿随意修改数值。
 */

const TIME_DELTA = 1 / 30.0

// ---------- 数学工具（old.py L462-488） ----------

export function calcAngle(a, b, c) {
  const radians = Math.atan2(c[1] - b[1], c[0] - b[0]) - Math.atan2(a[1] - b[1], a[0] - b[0])
  let angle = Math.abs(radians * 180.0 / Math.PI)
  if (angle > 180.0) {
    angle = 360 - angle
  }
  return angle
}

export function calcDistance(point1, point2) {
  const dx = point1[0] - point2[0]
  const dy = point1[1] - point2[1]
  return Math.sqrt(dx * dx + dy * dy)
}

// ---------- 卡路里（old.py L73-162） ----------

const EXERCISE_DATA = {
  'push-up': { met: 8.0, type: 'bodyweight', uses_rep_time: true, added_weight: false, weight_factor: 0 },
  squat: { met: 5.0, type: 'bodyweight', uses_rep_time: true, added_weight: false, weight_factor: 0 },
  'hammer curl': { met: 5.5, type: 'strength_arms', uses_rep_time: true, added_weight: true, weight_factor: 0.65 },
  'barbell biceps curl': { met: 6.0, type: 'strength_arms', uses_rep_time: true, added_weight: true, weight_factor: 0.7 },
  'shoulder press': { met: 6.5, type: 'strength_upper', uses_rep_time: true, added_weight: true, weight_factor: 0.8 }
}

const AGE_MODIFIERS = {
  under_30: { male: 1.00, female: 0.95 },
  '30_49': { male: 0.97, female: 0.92 },
  '50_69': { male: 0.93, female: 0.89 },
  '70_plus': { male: 0.90, female: 0.85 }
}

const REP_DURATIONS = {
  'push-up': 3.0,
  squat: 4.0,
  'hammer curl': 3.5,
  'barbell biceps curl': 3.5,
  'shoulder press': 4.0
}

// UserProfile 默认值（old.py L168-176）
const DEFAULT_USER_PROFILE = {
  bodyWeight: 70.0,
  age: 25,
  gender: 'male',
  addedWeights: {
    'hammer curl': 10.0,
    'barbell biceps curl': 20.0,
    'shoulder press': 15.0
  }
}

function getAgeCategory(age) {
  if (age < 30) return 'under_30'
  if (age < 50) return '30_49'
  if (age < 70) return '50_69'
  return '70_plus'
}

export function calcCaloriesPerRep(exercise, bodyWeightKg, age, gender, repDurationMin, addedWeightKg = 0) {
  const data = EXERCISE_DATA[exercise]
  if (!data) return 0
  const modifier = AGE_MODIFIERS[getAgeCategory(age)][gender.toLowerCase()]
  const effectiveWeight = (data.added_weight && addedWeightKg > 0)
    ? bodyWeightKg + data.weight_factor * addedWeightKg
    : bodyWeightKg
  return (data.met * 3.5 * effectiveWeight / 200) * repDurationMin * modifier
}

export function estimateRepDuration(exercise) {
  return REP_DURATIONS[exercise] || 3.0
}

// ---------- 特征工程（old.py L491-678，158 维/帧） ----------

/**
 * landmarksFlat: 长度 132 的扁平数组（33 点 × [x,y,z,visibility]）
 * state: { previousLandmarks, previousVelocities }（引擎内部维护）
 * 返回长度 158 的特征数组
 */
export function extractFeatures(landmarksFlat, state) {
  const landmarks = []
  const src = landmarksFlat.length >= 132 ? landmarksFlat.slice(0, 132) : padTo132(landmarksFlat)
  for (let i = 0; i < 33; i++) {
    landmarks.push([src[i * 4], src[i * 4 + 1], src[i * 4 + 2], src[i * 4 + 3]])
  }

  const features = []

  // 1. 归一化坐标特征（以髋部中心为原点、肩距为尺度）
  const hasFullBody = landmarks.length > 24
  if (hasFullBody) {
    const hipCenterX = (landmarks[23][0] + landmarks[24][0]) / 2
    const hipCenterY = (landmarks[23][1] + landmarks[24][1]) / 2
    let bodyScale = landmarks.length > 12 ? calcDistance(landmarks[11].slice(0, 2), landmarks[12].slice(0, 2)) : 1.0
    if (bodyScale < 0.01) bodyScale = 1.0
    for (let i = 0; i < 33; i++) {
      features.push(
        (landmarks[i][0] - hipCenterX) / bodyScale,
        (landmarks[i][1] - hipCenterY) / bodyScale,
        landmarks[i][2] / bodyScale
      )
    }
  } else {
    for (let i = 0; i < 33; i++) {
      features.push(landmarks[i][0], landmarks[i][1], landmarks[i][2])
    }
  }
  while (features.length < 99) features.push(0.0)

  // 2. 角度特征（左右肘、左右膝、脊柱、头颈）
  const angles = []
  angles.push(landmarks.length > 15 ? calcAngle(landmarks[11].slice(0, 2), landmarks[13].slice(0, 2), landmarks[15].slice(0, 2)) : 0.0)
  angles.push(landmarks.length > 16 ? calcAngle(landmarks[12].slice(0, 2), landmarks[14].slice(0, 2), landmarks[16].slice(0, 2)) : 0.0)
  angles.push(landmarks.length > 27 ? calcAngle(landmarks[23].slice(0, 2), landmarks[25].slice(0, 2), landmarks[27].slice(0, 2)) : 0.0)
  angles.push(landmarks.length > 28 ? calcAngle(landmarks[24].slice(0, 2), landmarks[26].slice(0, 2), landmarks[28].slice(0, 2)) : 0.0)
  if (landmarks.length > 28) {
    const shoulderCenter = [(landmarks[11][0] + landmarks[12][0]) / 2, (landmarks[11][1] + landmarks[12][1]) / 2]
    const hipCenter = [(landmarks[23][0] + landmarks[24][0]) / 2, (landmarks[23][1] + landmarks[24][1]) / 2]
    const kneeCenter = [(landmarks[25][0] + landmarks[26][0]) / 2, (landmarks[25][1] + landmarks[26][1]) / 2]
    angles.push(calcAngle(shoulderCenter, hipCenter, kneeCenter))
    angles.push(calcAngle(landmarks[0].slice(0, 2), shoulderCenter, hipCenter))
  } else {
    angles.push(0.0, 0.0)
  }
  features.push(...angles)

  // 3. 距离特征
  const distances = []
  distances.push(landmarks.length > 16 ? calcDistance(landmarks[15].slice(0, 2), landmarks[16].slice(0, 2)) : 0.0)
  if (landmarks.length > 28) {
    const shoulderCenter = [(landmarks[11][0] + landmarks[12][0]) / 2, (landmarks[11][1] + landmarks[12][1]) / 2]
    const hipCenter = [(landmarks[23][0] + landmarks[24][0]) / 2, (landmarks[23][1] + landmarks[24][1]) / 2]
    distances.push(
      calcDistance(landmarks[27].slice(0, 2), landmarks[28].slice(0, 2)),
      calcDistance(landmarks[11].slice(0, 2), landmarks[12].slice(0, 2)),
      calcDistance(landmarks[23].slice(0, 2), landmarks[24].slice(0, 2)),
      calcDistance(shoulderCenter, hipCenter),
      calcDistance(landmarks[15].slice(0, 2), landmarks[23].slice(0, 2)),
      calcDistance(landmarks[16].slice(0, 2), landmarks[24].slice(0, 2))
    )
  } else {
    distances.push(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
  }
  features.push(...distances)

  // 4. 速度特征（13 个关键点的 x/y 速度）
  const currentFlat = src
  const velocity = state.previousLandmarks
    ? diffScale(currentFlat, state.previousLandmarks, 1 / TIME_DELTA)
    : null
  const velocityIndices = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
  const keyVelocities = []
  for (const idx of velocityIndices) {
    if (velocity && idx * 4 + 3 < velocity.length) {
      keyVelocities.push(velocity[idx * 4], velocity[idx * 4 + 1])
    } else {
      keyVelocities.push(0.0, 0.0)
    }
  }
  features.push(...keyVelocities.slice(0, 26))

  // 5. 加速度特征（9 个关键点的 x/y 加速度）
  const accelerationIndices = [0, 11, 12, 15, 16, 23, 24, 27, 28]
  const keyAccelerations = []
  if (state.previousVelocities && velocity) {
    const acceleration = diffScale(velocity, state.previousVelocities, 1 / TIME_DELTA)
    for (const idx of accelerationIndices) {
      if (idx * 4 + 3 < acceleration.length) {
        keyAccelerations.push(acceleration[idx * 4], acceleration[idx * 4 + 1])
      } else {
        keyAccelerations.push(0.0, 0.0)
      }
    }
    state.previousVelocities = velocity
  } else {
    for (const idx of accelerationIndices) {
      keyAccelerations.push(0.0, 0.0)
    }
    if (state.previousLandmarks) {
      state.previousVelocities = diffScale(currentFlat, state.previousLandmarks, 1 / TIME_DELTA)
    }
  }
  features.push(...keyAccelerations.slice(0, 18))

  state.previousLandmarks = currentFlat.slice()

  // 6. 对称性特征
  const symmetry = []
  symmetry.push(landmarks.length > 16
    ? Math.abs(calcDistance(landmarks[11].slice(0, 2), landmarks[15].slice(0, 2)) - calcDistance(landmarks[12].slice(0, 2), landmarks[16].slice(0, 2)))
    : 0.0)
  symmetry.push(landmarks.length > 28
    ? Math.abs(calcDistance(landmarks[23].slice(0, 2), landmarks[27].slice(0, 2)) - calcDistance(landmarks[24].slice(0, 2), landmarks[28].slice(0, 2)))
    : 0.0)
  features.push(...symmetry)

  return features
}

function padTo132(arr) {
  const padded = new Array(132).fill(0)
  for (let i = 0; i < Math.min(132, arr.length); i++) padded[i] = arr[i]
  return padded
}

function diffScale(current, previous, factor) {
  const out = new Array(current.length)
  for (let i = 0; i < current.length; i++) {
    out[i] = (current[i] - previous[i]) * factor
  }
  return out
}

// ---------- 计数状态机（old.py L681-1320） ----------

const TARGET_EXERCISES = [
  'barbell biceps curl', 'hammer curl', 'push-up', 'shoulder press', 'squat'
]

const EXERCISE_CONFIGS = {
  'barbell biceps curl': {
    key_joints: [13, 14, 15, 16],
    angle_joints: [[11, 13, 15], [12, 14, 16]],
    count_on_angle_change: true,
    angle_threshold: 30,
    min_angle: 70,
    max_angle: 160,
    warmup_frames: 5
  },
  'hammer curl': {
    key_joints: [13, 14, 15, 16],
    angle_joints: [[11, 13, 15], [12, 14, 16]],
    count_on_angle_change: true,
    angle_threshold: 20,
    min_angle: 60,
    max_angle: 170,
    warmup_frames: 4,
    stable_frames_required: 1,
    transition_frames_required: 1,
    enhanced_detection: true
  },
  'push-up': {
    key_joints: [11, 12, 13, 14, 15, 16],
    angle_joints: [[11, 13, 15], [12, 14, 16]],
    count_on_angle_change: true,
    angle_threshold: 20,
    min_angle: 70,
    max_angle: 140,
    warmup_frames: 5,
    stable_frames_required: 1,
    transition_frames_required: 1,
    use_enhanced_detection: true
  },
  'shoulder press': {
    key_joints: [11, 12, 13, 14, 15, 16],
    angle_joints: [[11, 13, 15], [12, 14, 16]],
    count_on_angle_change: true,
    angle_threshold: 30,
    min_angle: 60,
    max_angle: 160,
    warmup_frames: 5
  },
  squat: {
    key_joints: [23, 24, 25, 26, 27, 28],
    angle_joints: [[23, 25, 27], [24, 26, 28]],
    count_on_angle_change: true,
    angle_threshold: 40,
    min_angle: 70,
    max_angle: 170,
    warmup_frames: 5
  }
}

function createDeque(maxLen) {
  const items = []
  return {
    push(value) {
      items.push(value)
      if (items.length > maxLen) items.shift()
    },
    get length() {
      return items.length
    },
    clear() {
      items.length = 0
    },
    toArray() {
      return items
    },
    last(n = 1) {
      return items[items.length - n]
    }
  }
}

export class ExerciseEngine {
  /**
   * @param options
   *  - scaler: { mean: number[158], scale: number[158] }（scaler.pkl 导出）
   *  - labels: string[]（label_encoder.classes_，与 ONNX 输出下标对应）
   *  - sequenceLength: 默认 30
   *  - onnxRun: async (scaledSequence: Float32Array(30*158)) => Float32Array/Array(numClasses)
   */
  constructor(options = {}) {
    const scaler = options.scaler
    if (!scaler || !Array.isArray(scaler.mean) || !Array.isArray(scaler.scale)) {
      throw new Error('ExerciseEngine requires scaler {mean, scale}')
    }
    this.scalerMean = scaler.mean
    this.scalerScale = scaler.scale
    this.labels = options.labels && options.labels.length
      ? options.labels
      : TARGET_EXERCISES.slice()
    this.sequenceLength = options.sequenceLength || 30
    this.onnxRun = options.onnxRun

    this.featureState = { previousLandmarks: null, previousVelocities: null }
    this.featureBuffer = createDeque(this.sequenceLength)

    // ExerciseCounterOptimized 状态
    this.userProfile = DEFAULT_USER_PROFILE
    this.confidenceThreshold = 0.55
    this.counts = {}
    this.calories = {}
    this.exerciseStates = {}
    this.positionTrackers = {}
    this.repStartTimes = {}
    this.repDurations = {}
    this.exerciseSpecificData = {}
    for (const exercise of TARGET_EXERCISES) {
      this.counts[exercise] = 0
      this.calories[exercise] = 0.0
      this.exerciseStates[exercise] = 'none'
      this.positionTrackers[exercise] = createDeque(20)
      this.repStartTimes[exercise] = null
      this.repDurations[exercise] = createDeque(10)
      this.exerciseSpecificData[exercise] = {
        last_key_angle: null,
        last_key_height: null,
        min_angle_seen: Infinity,
        max_angle_seen: 0,
        min_height_seen: Infinity,
        max_height_seen: 0,
        stable_frames: 0,
        transition_frames: 0
      }
    }
  }

  // ----- 特征与分类（old.py L1546-1591） -----

  /** 每帧调用：提取特征并写入滑窗，返回滑窗是否已满 */
  feed(landmarksFlat) {
    const features = extractFeatures(landmarksFlat, this.featureState)
    this.featureBuffer.push(features)
    return this.featureBuffer.length >= this.sequenceLength
  }

  /** 滑窗已满时调用：归一化 + ONNX 推理 + softmax/argmax */
  async classify() {
    if (this.featureBuffer.length < this.sequenceLength || !this.onnxRun) {
      return null
    }
    const sequence = this.featureBuffer.toArray()
    const dims = this.sequenceLength * this.scalerMean.length
    const scaled = new Float32Array(dims)
    let offset = 0
    for (let t = 0; t < this.sequenceLength; t++) {
      const frame = sequence[t]
      for (let j = 0; j < this.scalerMean.length; j++) {
        scaled[offset++] = (frame[j] - this.scalerMean[j]) / this.scalerScale[j]
      }
    }
    try {
      const logits = await this.onnxRun(scaled)
      return softmaxArgmax(logits, this.labels)
    } catch (e) {
      return null
    }
  }

  // ----- 计数入口（old.py L1290-1299 + L821-833） -----

  updateCounts(predictedExercise, confidence, landmarksFlat) {
    if (confidence < this.confidenceThreshold) {
      return
    }
    if (TARGET_EXERCISES.indexOf(predictedExercise) >= 0) {
      if (this.detectRepCompletion(predictedExercise, landmarksFlat)) {
        this.counts[predictedExercise] += 1
        this.endRepTimerAndCalculateCalories(predictedExercise)
      }
    }
  }

  detectRepCompletion(exercise, landmarksFlat) {
    if (!EXERCISE_CONFIGS[exercise]) {
      return false
    }
    if (exercise === 'push-up') {
      return this.detectPushupRepEnhanced(exercise, landmarksFlat)
    }
    if (exercise === 'hammer curl') {
      return this.detectHammerCurlRepEnhanced(exercise, landmarksFlat)
    }
    return this.detectAngleBasedRepImproved(exercise, landmarksFlat, EXERCISE_CONFIGS[exercise])
  }

  // ----- 增强版 hammer curl（old.py L835-978） -----

  detectHammerCurlRepEnhanced(exercise, landmarksFlat) {
    if (landmarksFlat.length < 132) return false
    const l = reshapeLandmarks(landmarksFlat)
    const config = EXERCISE_CONFIGS[exercise]
    const data = this.exerciseSpecificData[exercise]

    const angles = []
    let leftAngle = null
    let rightAngle = null

    if (norm2d(l[11], l[13]) > 0.01 && norm2d(l[13], l[15]) > 0.01) {
      leftAngle = calcAngle(l[11], l[13], l[15])
      angles.push(leftAngle)
    }
    if (norm2d(l[12], l[14]) > 0.01 && norm2d(l[14], l[16]) > 0.01) {
      rightAngle = calcAngle(l[12], l[14], l[16])
      angles.push(rightAngle)
    }
    if (!angles.length) return false

    let currentAngle
    if (angles.length === 2) {
      const leftVar = Math.abs(leftAngle - (data.last_left_angle !== undefined ? data.last_left_angle : leftAngle))
      const rightVar = Math.abs(rightAngle - (data.last_right_angle !== undefined ? data.last_right_angle : rightAngle))
      if (leftVar >= rightVar) {
        currentAngle = leftAngle
        data.primary_arm = 'left'
      } else {
        currentAngle = rightAngle
        data.primary_arm = 'right'
      }
      data.last_left_angle = leftAngle
      data.last_right_angle = rightAngle
    } else {
      currentAngle = angles[0]
    }

    this.positionTrackers[exercise].push(currentAngle)
    if (this.positionTrackers[exercise].length < getWarmupFrames(exercise, 4)) return false

    const smoothedAngle = smoothAngleSequence(this.positionTrackers[exercise].toArray(), 3)
    data.min_angle_seen = Math.min(data.min_angle_seen, smoothedAngle)
    data.max_angle_seen = Math.max(data.max_angle_seen, smoothedAngle)

    const angleRange = data.max_angle_seen - data.min_angle_seen
    let dynamicMax
    let dynamicMin
    if (angleRange > 25) {
      dynamicMax = data.min_angle_seen + angleRange * 0.75
      dynamicMin = data.min_angle_seen + angleRange * 0.35
    } else {
      dynamicMax = config.max_angle
      dynamicMin = config.min_angle
    }

    let angleVelocity = 0
    if (this.positionTrackers[exercise].length >= 3) {
      const recent = this.positionTrackers[exercise].toArray().slice(-3)
      angleVelocity = recent[recent.length - 1] - recent[0]
    }

    return this.detectHammerCurlWithVelocity(exercise, smoothedAngle, angleVelocity, dynamicMax, dynamicMin)
  }

  detectHammerCurlWithVelocity(exercise, angle, angleVelocity, maxThreshold, minThreshold) {
    const data = this.exerciseSpecificData[exercise]
    const transitionFramesRequired = getTransitionFramesRequired(exercise, 1)
    const stabilityMargin = 8
    const velocityThreshold = 1.5
    let state = this.exerciseStates[exercise]

    if (state === 'none') {
      if (angle > maxThreshold - 15) {
        this.exerciseStates[exercise] = 'extended'
        data.stable_frames = 0
        this.startRepTimer(exercise)
        return false
      }
    } else if (state === 'extended') {
      if (angle > maxThreshold - stabilityMargin) {
        data.stable_frames += 1
      } else {
        data.stable_frames = Math.max(0, data.stable_frames - 1)
      }
      if (angle < maxThreshold - 12 && angleVelocity < -velocityThreshold) {
        this.exerciseStates[exercise] = 'flexing'
        data.transition_frames = 0
        return false
      }
    } else if (state === 'flexing') {
      data.transition_frames += 1
      if (angle > maxThreshold - 10 && angleVelocity > velocityThreshold) {
        this.exerciseStates[exercise] = 'extended'
        return false
      }
      if (angle < minThreshold + 15 && data.transition_frames >= transitionFramesRequired) {
        this.exerciseStates[exercise] = 'flexed'
        data.stable_frames = 0
        return false
      }
    } else if (state === 'flexed') {
      if (angle < minThreshold + stabilityMargin) {
        data.stable_frames += 1
      } else {
        data.stable_frames = Math.max(0, data.stable_frames - 1)
      }
      if (angle > minThreshold + 12 && angleVelocity > velocityThreshold) {
        this.exerciseStates[exercise] = 'extending'
        data.transition_frames = 0
        return false
      }
    } else if (state === 'extending') {
      data.transition_frames += 1
      if (angle < minThreshold + 10 && angleVelocity < -velocityThreshold) {
        this.exerciseStates[exercise] = 'flexed'
        return false
      }
      if (angle > maxThreshold - 15 && data.transition_frames >= transitionFramesRequired) {
        this.exerciseStates[exercise] = 'extended'
        data.stable_frames = 0
        return true
      }
    }
    return false
  }

  // ----- 通用角度计数（old.py L980-1074, L1214-1288） -----

  detectAngleBasedRepImproved(exercise, landmarksFlat, config) {
    if (landmarksFlat.length < 132) return false
    const l = reshapeLandmarks(landmarksFlat)

    const angles = []
    for (const joints of config.angle_joints) {
      const a = l[joints[0]]
      const b = l[joints[1]]
      const c = l[joints[2]]
      if (norm2d(a, b) > 0.01 && norm2d(b, c) > 0.01) {
        angles.push(calcAngle(a, b, c))
      }
    }
    if (!angles.length) return false

    const currentAngle = mean(angles)
    this.positionTrackers[exercise].push(currentAngle)
    if (this.positionTrackers[exercise].length < getWarmupFrames(exercise, 5)) return false

    const data = this.exerciseSpecificData[exercise]
    const smoothedAngle = smoothAngleSequence(this.positionTrackers[exercise].toArray())
    data.min_angle_seen = Math.min(data.min_angle_seen, smoothedAngle)
    data.max_angle_seen = Math.max(data.max_angle_seen, smoothedAngle)

    let dynamicMax
    let dynamicMin
    if (data.max_angle_seen - data.min_angle_seen > 40) {
      const range = data.max_angle_seen - data.min_angle_seen
      dynamicMax = data.min_angle_seen + range * 0.8
      dynamicMin = data.min_angle_seen + range * 0.3
    } else {
      dynamicMax = config.max_angle
      dynamicMin = config.min_angle
    }

    if (exercise === 'barbell biceps curl') {
      return this.detectCurlRep(exercise, smoothedAngle, dynamicMax, dynamicMin)
    }
    if (exercise === 'shoulder press') {
      return this.detectShoulderPressRep(exercise, smoothedAngle, dynamicMax, dynamicMin)
    }
    if (exercise === 'squat') {
      return this.detectSquatRep(exercise, smoothedAngle, dynamicMax, dynamicMin)
    }
    return false
  }

  detectCurlRep(exercise, angle, maxThreshold, minThreshold) {
    const data = this.exerciseSpecificData[exercise]
    const state = this.exerciseStates[exercise]

    if (state === 'none') {
      if (angle > maxThreshold - 10) {
        this.exerciseStates[exercise] = 'extended'
        data.stable_frames = 0
        this.startRepTimer(exercise)
      }
    } else if (state === 'extended') {
      if (angle > maxThreshold - 10) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle < minThreshold + 20) {
        this.exerciseStates[exercise] = 'flexing'
        data.transition_frames = 0
      }
    } else if (state === 'flexing') {
      data.transition_frames += 1
      if (angle < minThreshold + 10) {
        this.exerciseStates[exercise] = 'flexed'
        data.stable_frames = 0
      }
    } else if (state === 'flexed') {
      if (angle < minThreshold + 15) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle > maxThreshold - 20) {
        this.exerciseStates[exercise] = 'extending'
        data.transition_frames = 0
      }
    } else if (state === 'extending') {
      data.transition_frames += 1
      if (angle > maxThreshold - 10) {
        this.exerciseStates[exercise] = 'extended'
        return true
      }
    }
    return false
  }

  detectShoulderPressRep(exercise, angle, maxThreshold, minThreshold) {
    const data = this.exerciseSpecificData[exercise]
    const state = this.exerciseStates[exercise]

    if (state === 'none') {
      if (angle < minThreshold + 20) {
        this.exerciseStates[exercise] = 'down'
        data.stable_frames = 0
        this.startRepTimer(exercise)
      }
    } else if (state === 'down') {
      if (angle < minThreshold + 25) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle > minThreshold + 40) {
        this.exerciseStates[exercise] = 'pressing_up'
        data.transition_frames = 0
      }
    } else if (state === 'pressing_up') {
      data.transition_frames += 1
      if (angle > maxThreshold - 20) {
        this.exerciseStates[exercise] = 'up'
        data.stable_frames = 0
      }
    } else if (state === 'up') {
      if (angle > maxThreshold - 25) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle < maxThreshold - 40) {
        this.exerciseStates[exercise] = 'pressing_down'
        data.transition_frames = 0
      }
    } else if (state === 'pressing_down') {
      data.transition_frames += 1
      if (angle < minThreshold + 20) {
        this.exerciseStates[exercise] = 'down'
        return true
      }
    }
    return false
  }

  detectSquatRep(exercise, angle, maxThreshold, minThreshold) {
    const data = this.exerciseSpecificData[exercise]
    const state = this.exerciseStates[exercise]

    if (state === 'none') {
      if (angle > maxThreshold - 10) {
        this.exerciseStates[exercise] = 'standing'
        data.stable_frames = 0
        this.startRepTimer(exercise)
      }
    } else if (state === 'standing') {
      if (angle > maxThreshold - 15) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle < maxThreshold - 30) {
        this.exerciseStates[exercise] = 'squatting_down'
        data.transition_frames = 0
      }
    } else if (state === 'squatting_down') {
      data.transition_frames += 1
      if (angle < minThreshold + 20) {
        this.exerciseStates[exercise] = 'squatting'
        data.stable_frames = 0
      }
    } else if (state === 'squatting') {
      if (angle < minThreshold + 25) {
        data.stable_frames += 1
      } else {
        data.stable_frames = 0
      }
      if (angle > minThreshold + 40) {
        this.exerciseStates[exercise] = 'standing_up'
        data.transition_frames = 0
      }
    } else if (state === 'standing_up') {
      data.transition_frames += 1
      if (angle > maxThreshold - 10) {
        this.exerciseStates[exercise] = 'standing'
        return true
      }
    }
    return false
  }

  // ----- 增强版 push-up（old.py L1076-1212） -----

  detectPushupRepEnhanced(exercise, landmarksFlat) {
    if (landmarksFlat.length < 132) return false
    const l = reshapeLandmarks(landmarksFlat)
    const config = EXERCISE_CONFIGS[exercise]

    const angles = []
    for (const joints of config.angle_joints) {
      const a = l[joints[0]]
      const b = l[joints[1]]
      const c = l[joints[2]]
      if (norm2d(a, b) > 0.01 && norm2d(b, c) > 0.01) {
        angles.push(calcAngle(a, b, c))
      }
    }
    if (!angles.length) return false

    const armAngle = mean(angles)

    let bodyHeight = 0
    try {
      const shoulderCenterY = (l[11][1] + l[12][1]) / 2
      const wristCenterY = (l[15][1] + l[16][1]) / 2
      bodyHeight = Math.abs(shoulderCenterY - wristCenterY)
    } catch (e) {
      bodyHeight = 0
    }

    const normalizedHeight = Math.min(180, Math.max(0, bodyHeight * 1000))
    const combinedScore = armAngle * 0.7 + normalizedHeight * 0.3

    this.positionTrackers[exercise].push(combinedScore)
    if (this.positionTrackers[exercise].length < getWarmupFrames(exercise, 5)) return false

    const data = this.exerciseSpecificData[exercise]
    const smoothedScore = smoothAngleSequence(this.positionTrackers[exercise].toArray())

    data.min_angle_seen = Math.min(data.min_angle_seen, smoothedScore)
    data.max_angle_seen = Math.max(data.max_angle_seen, smoothedScore)

    let dynamicMax
    let dynamicMin
    if (data.max_angle_seen - data.min_angle_seen > 30) {
      const range = data.max_angle_seen - data.min_angle_seen
      dynamicMax = data.min_angle_seen + range * 0.75
      dynamicMin = data.min_angle_seen + range * 0.35
    } else {
      dynamicMax = 120
      dynamicMin = 80
    }

    return this.detectPushupRepImproved(exercise, smoothedScore, dynamicMax, dynamicMin)
  }

  detectPushupRepImproved(exercise, score, maxThreshold, minThreshold) {
    const data = this.exerciseSpecificData[exercise]
    const stableFramesRequired = getStableFramesRequired(exercise, 1)
    const transitionFramesRequired = getTransitionFramesRequired(exercise, 1)
    const state = this.exerciseStates[exercise]

    const recentScores = this.positionTrackers[exercise].toArray().slice(-10)
    if (recentScores.length < 5) return false

    let scoreVelocity = 0
    if (recentScores.length >= 3) {
      scoreVelocity = recentScores[recentScores.length - 1] - recentScores[recentScores.length - 3]
    }

    if (state === 'none') {
      if (score > maxThreshold - 10) {
        this.exerciseStates[exercise] = 'up'
        data.stable_frames = 0
        data.transition_frames = 0
        this.startRepTimer(exercise)
      }
    } else if (state === 'up') {
      if (score > maxThreshold - 15) {
        data.stable_frames += 1
      } else {
        data.stable_frames = Math.max(0, data.stable_frames - 1)
      }
      if (data.stable_frames >= stableFramesRequired && score < maxThreshold - 20 && scoreVelocity < -2) {
        this.exerciseStates[exercise] = 'going_down'
        data.transition_frames = 0
        data.stable_frames = 0
      }
    } else if (state === 'going_down') {
      data.transition_frames += 1
      if (score > maxThreshold - 15 && scoreVelocity > 1) {
        this.exerciseStates[exercise] = 'up'
        data.stable_frames = 0
        return false
      }
      if (score < minThreshold + 25 && data.transition_frames >= transitionFramesRequired) {
        this.exerciseStates[exercise] = 'down'
        data.stable_frames = 0
        data.transition_frames = 0
      }
    } else if (state === 'down') {
      if (score < minThreshold + 30) {
        data.stable_frames += 1
      } else {
        data.stable_frames = Math.max(0, data.stable_frames - 1)
      }
      if (data.stable_frames >= stableFramesRequired && score > minThreshold + 35 && scoreVelocity > 2) {
        this.exerciseStates[exercise] = 'going_up'
        data.transition_frames = 0
        data.stable_frames = 0
      }
    } else if (state === 'going_up') {
      data.transition_frames += 1
      if (score < minThreshold + 30 && scoreVelocity < -1) {
        this.exerciseStates[exercise] = 'down'
        data.stable_frames = 0
        return false
      }
      if (score > maxThreshold - 15 && data.transition_frames >= transitionFramesRequired) {
        this.exerciseStates[exercise] = 'up'
        data.stable_frames = 0
        data.transition_frames = 0
        return true
      }
    }
    return false
  }

  // ----- rep 计时与卡路里（old.py L794-819） -----

  startRepTimer(exercise) {
    this.repStartTimes[exercise] = Date.now()
  }

  endRepTimerAndCalculateCalories(exercise) {
    let repDurationSec
    if (this.repStartTimes[exercise] == null) {
      repDurationSec = estimateRepDuration(exercise)
    } else {
      repDurationSec = (Date.now() - this.repStartTimes[exercise]) / 1000
      this.repStartTimes[exercise] = null
    }
    this.repDurations[exercise].push(repDurationSec)

    const repDurationMin = repDurationSec / 60.0
    const addedWeight = this.userProfile.addedWeights[exercise] || 0
    const caloriesBurned = calcCaloriesPerRep(
      exercise,
      this.userProfile.bodyWeight,
      this.userProfile.age,
      this.userProfile.gender,
      repDurationMin,
      addedWeight
    )
    this.calories[exercise] += caloriesBurned
    return caloriesBurned
  }

  // ----- 统计与响应（old.py L1593-1613 + server.py L919-962） -----

  getRuntimeStats(predictedExercise = null, confidence = 0.0) {
    return {
      exercise: predictedExercise,
      confidence: Number(confidence),
      counts: { ...this.counts },
      calories: { ...this.calories },
      total_reps: Object.values(this.counts).reduce((sum, n) => sum + n, 0),
      total_calories: Object.values(this.calories).reduce((sum, n) => sum + n, 0.0)
    }
  }

  /**
   * 输出与后端 /api/realtime_frame 完全同构的响应对象
   * landmarksFlat: 长度 132 的扁平数组；可为 null
   */
  buildDetectResponse(predictedExercise, confidence, landmarksFlat, fps = 0) {
    const stats = this.getRuntimeStats(predictedExercise, confidence)
    return {
      exercise: predictedExercise || '未检测到',
      confidence: Number(confidence) || 0.0,
      reps: predictedExercise ? (stats.counts[predictedExercise] || 0) : 0,
      calories: predictedExercise ? Number(stats.calories[predictedExercise] || 0.0) : 0.0,
      total_reps: stats.total_reps,
      total_calories: stats.total_calories,
      accuracy: Number(confidence) * 100,
      counts: stats.counts,
      calories_by_exercise: stats.calories,
      landmarks: serializeLandmarks(landmarksFlat),
      fps
    }
  }

  reset() {
    this.featureState = { previousLandmarks: null, previousVelocities: null }
    this.featureBuffer.clear()
    for (const exercise of TARGET_EXERCISES) {
      this.counts[exercise] = 0
      this.calories[exercise] = 0.0
      this.exerciseStates[exercise] = 'none'
      this.positionTrackers[exercise].clear()
      this.repStartTimes[exercise] = null
      this.repDurations[exercise].clear()
    }
  }
}

// ---------- 内部工具 ----------

function getWarmupFrames(exercise, defaultFrames = 5) {
  const config = EXERCISE_CONFIGS[exercise]
  return (config && config.warmup_frames !== undefined) ? config.warmup_frames : defaultFrames
}

function getStableFramesRequired(exercise, defaultFrames = 1) {
  const config = EXERCISE_CONFIGS[exercise]
  return (config && config.stable_frames_required !== undefined) ? config.stable_frames_required : defaultFrames
}

function getTransitionFramesRequired(exercise, defaultFrames = 1) {
  const config = EXERCISE_CONFIGS[exercise]
  return (config && config.transition_frames_required !== undefined) ? config.transition_frames_required : defaultFrames
}

function smoothAngleSequence(angles, windowSize = 5) {
  if (angles.length < windowSize) {
    return angles.length ? angles[angles.length - 1] : 0
  }
  const recent = angles.slice(-windowSize)
  return mean(recent)
}

function mean(values) {
  let sum = 0
  for (const v of values) sum += v
  return values.length ? sum / values.length : 0
}

function reshapeLandmarks(landmarksFlat) {
  const out = []
  const src = landmarksFlat.length >= 132 ? landmarksFlat.slice(0, 132) : padTo132(landmarksFlat)
  for (let i = 0; i < 33; i++) {
    out.push([src[i * 4], src[i * 4 + 1], src[i * 4 + 2], src[i * 4 + 3]])
  }
  return out
}

function norm2d(a, b) {
  const dx = a[0] - b[0]
  const dy = a[1] - b[1]
  return Math.sqrt(dx * dx + dy * dy)
}

function softmaxArgmax(logits, labels) {
  let maxVal = -Infinity
  for (const v of logits) {
    if (v > maxVal) maxVal = v
  }
  let sum = 0
  const exps = []
  for (const v of logits) {
    const e = Math.exp(v - maxVal)
    exps.push(e)
    sum += e
  }
  let bestIdx = 0
  let bestVal = -Infinity
  for (let i = 0; i < exps.length; i++) {
    const p = exps[i] / sum
    if (p > bestVal) {
      bestVal = p
      bestIdx = i
    }
  }
  return { exercise: labels[bestIdx], confidence: bestVal }
}

function serializeLandmarks(landmarksFlat) {
  if (!landmarksFlat) return []
  const src = landmarksFlat.length >= 132 ? landmarksFlat.slice(0, 132) : padTo132(landmarksFlat)
  const result = []
  for (let i = 0; i < 33; i++) {
    result.push({
      x: Number(src[i * 4]),
      y: Number(src[i * 4 + 1]),
      z: Number(src[i * 4 + 2]),
      visibility: Number(src[i * 4 + 3])
    })
  }
  return result
}
