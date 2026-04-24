import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np
import pickle
import json
import os
from collections import deque
import time
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
from scipy.signal import savgol_filter
import onnxruntime as ort

try:
    import mediapipe as mp
except ImportError:
    mp = None

try:
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
except ImportError:
    mp_python = None
    mp_vision = None

warnings.filterwarnings('ignore')


def draw_text_with_background(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX,
                              font_scale=0.7, color=(255, 255, 255), thickness=2,
                              bg_color=(0, 0, 0), padding=5):
    """绘制带背景的文字，提高可读性"""
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = pos
    bg_x1 = x - padding
    bg_y1 = y - text_height - padding
    bg_x2 = x + text_width + padding
    bg_y2 = y + baseline + padding

    cv2.rectangle(img, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)

    outline_thickness = thickness + 1
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                cv2.putText(img, text, (x + dx, y + dy), font, font_scale,
                            (0, 0, 0), outline_thickness, cv2.LINE_AA)

    cv2.putText(img, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

    return text_height + baseline + padding * 2


def draw_text_enhanced(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale=0.6, color=(255, 255, 255), thickness=2):
    """增强版文字绘制，带描边效果"""
    x, y = pos

    outline_thickness = max(1, thickness)
    cv2.putText(img, text, (x - 1, y - 1), font, font_scale, (0, 0, 0), outline_thickness, cv2.LINE_AA)
    cv2.putText(img, text, (x + 1, y - 1), font, font_scale, (0, 0, 0), outline_thickness, cv2.LINE_AA)
    cv2.putText(img, text, (x - 1, y + 1), font, font_scale, (0, 0, 0), outline_thickness, cv2.LINE_AA)
    cv2.putText(img, text, (x + 1, y + 1), font, font_scale, (0, 0, 0), outline_thickness, cv2.LINE_AA)

    cv2.putText(img, text, pos, font, font_scale, color, thickness, cv2.LINE_AA)


class CalorieCalculator:
    """卡路里计算器"""

    def __init__(self):
        self.exercise_data = {
            'push-up': {
                'met': 8.0,
                'type': 'bodyweight',
                'uses_rep_time': True,
                'added_weight': False,
                'weight_factor': 0
            },
            'squat': {
                'met': 5.0,
                'type': 'bodyweight',
                'uses_rep_time': True,
                'added_weight': False,
                'weight_factor': 0
            },
            'hammer curl': {
                'met': 5.5,
                'type': 'strength_arms',
                'uses_rep_time': True,
                'added_weight': True,
                'weight_factor': 0.65
            },
            'barbell biceps curl': {
                'met': 6.0,
                'type': 'strength_arms',
                'uses_rep_time': True,
                'added_weight': True,
                'weight_factor': 0.7
            },
            'shoulder press': {
                'met': 6.5,
                'type': 'strength_upper',
                'uses_rep_time': True,
                'added_weight': True,
                'weight_factor': 0.8
            }
        }

        self.modifiers = {
            'under_30': {'male': 1.00, 'female': 0.95},
            '30_49': {'male': 0.97, 'female': 0.92},
            '50_69': {'male': 0.93, 'female': 0.89},
            '70_plus': {'male': 0.90, 'female': 0.85}
        }

    def get_age_category(self, age):
        if age < 30:
            return 'under_30'
        elif age < 50:
            return '30_49'
        elif age < 70:
            return '50_69'
        else:
            return '70_plus'

    def get_modifier(self, age, gender):
        age_category = self.get_age_category(age)
        return self.modifiers[age_category][gender.lower()]

    def calculate_calories_per_rep(self, exercise, body_weight_kg, age, gender,
                                   rep_duration_min, added_weight_kg=0):
        if exercise not in self.exercise_data:
            return 0

        data = self.exercise_data[exercise]
        met = data['met']
        modifier = self.get_modifier(age, gender)

        if data['added_weight'] and added_weight_kg > 0:
            effective_weight = body_weight_kg + data['weight_factor'] * added_weight_kg
        else:
            effective_weight = body_weight_kg

        calories_per_rep = (met * 3.5 * effective_weight / 200) * rep_duration_min * modifier
        return calories_per_rep

    def estimate_rep_duration(self, exercise):
        durations = {
            'push-up': 3.0,
            'squat': 4.0,
            'hammer curl': 3.5,
            'barbell biceps curl': 3.5,
            'shoulder press': 4.0
        }
        return durations.get(exercise, 3.0)


class UserProfile:
    """用户配置文件"""

    def __init__(self):
        self.body_weight = 70.0
        self.age = 25
        self.gender = 'male'
        self.added_weights = {
            'hammer curl': 10.0,
            'barbell biceps curl': 20.0,
            'shoulder press': 15.0
        }
        self.profile_loaded = False

    def load_from_input(self):
        """从用户输入加载配置"""
        print("\n=== 用户信息设置 ===")

        try:
            weight_input = input("请输入您的体重(kg) [默认: 70]: ").strip()
            if weight_input:
                self.body_weight = float(weight_input)

            age_input = input("请输入您的年龄 [默认: 25]: ").strip()
            if age_input:
                self.age = int(age_input)

            gender_input = input("请输入您的性别 (male/female) [默认: male]: ").strip().lower()
            if gender_input in ['male', 'female']:
                self.gender = gender_input

            print("\n=== 力量训练重量设置 ===")
            print("请设置各项力量训练的重量(kg)，直接回车使用默认值：")

            for exercise in self.added_weights:
                default_weight = self.added_weights[exercise]
                weight_input = input(f"{exercise} [默认: {default_weight}kg]: ").strip()
                if weight_input:
                    try:
                        self.added_weights[exercise] = float(weight_input)
                    except ValueError:
                        print(f"无效输入，使用默认值 {default_weight}kg")

            self.profile_loaded = True
            self.print_profile()

        except ValueError as e:
            print(f"输入错误: {e}")
            print("使用默认设置")
            self.profile_loaded = True

    def print_profile(self):
        print(f"\n=== 用户配置确认 ===")
        print(f"体重: {self.body_weight}kg")
        print(f"年龄: {self.age}岁")
        print(f"性别: {self.gender}")
        print(f"力量训练重量:")
        for exercise, weight in self.added_weights.items():
            print(f"  {exercise}: {weight}kg")
        print("=" * 30)


class AttentionLayer(nn.Module):
    def __init__(self, hidden_dim):
        super(AttentionLayer, self).__init__()
        self.hidden_dim = hidden_dim
        self.attention = nn.Linear(hidden_dim, 1)

    def forward(self, lstm_output):
        attention_weights = torch.softmax(self.attention(lstm_output), dim=1)
        context = torch.sum(attention_weights * lstm_output, dim=1)
        return context, attention_weights


class CNNFeatureExtractor(nn.Module):
    def __init__(self, input_dim, cnn_filters=[64, 128, 256]):
        super(CNNFeatureExtractor, self).__init__()
        self.conv_layers = nn.ModuleList()
        in_channels = input_dim

        for out_channels in cnn_filters:
            self.conv_layers.append(
                nn.Sequential(
                    nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1),
                    nn.BatchNorm1d(out_channels),
                    nn.ReLU(),
                    nn.MaxPool1d(kernel_size=2, stride=1, padding=1),
                    nn.Dropout(0.2)
                )
            )
            in_channels = out_channels

        self.output_dim = cnn_filters[-1]

    def forward(self, x):
        x = x.transpose(1, 2)
        for conv_layer in self.conv_layers:
            x = conv_layer(x)
        x = x.transpose(1, 2)
        return x


class EnhancedExerciseClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes, dropout=0.3):
        super(EnhancedExerciseClassifier, self).__init__()

        self.cnn = CNNFeatureExtractor(input_dim, cnn_filters=[64, 128, 128])
        cnn_output_dim = self.cnn.output_dim

        self.bilstm = nn.LSTM(
            input_size=cnn_output_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )

        self.attention = AttentionLayer(hidden_dim * 2)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, num_classes)

        self.layer_norm1 = nn.LayerNorm(hidden_dim)
        self.layer_norm2 = nn.LayerNorm(hidden_dim // 2)
        self.residual_fc = nn.Linear(hidden_dim * 2, hidden_dim)

    def forward(self, x):
        cnn_features = self.cnn(x)
        lstm_out, _ = self.bilstm(cnn_features)
        context, attention_weights = self.attention(lstm_out)

        out = self.dropout(context)
        fc1_out = self.fc1(out)
        fc1_out = self.layer_norm1(fc1_out)
        fc1_out = F.relu(fc1_out)

        residual = self.residual_fc(context)
        fc1_out = fc1_out + residual
        out = self.dropout(fc1_out)

        out = self.fc2(out)
        out = self.layer_norm2(out)
        out = F.relu(out)
        out = self.dropout(out)

        out = self.fc3(out)
        return out


class RealtimeFeatureExtractor:
    """实时特征提取器 - 电脑版本"""

    def __init__(self, model_path=None):
        if mp is None:
            raise ImportError(
                "未安装 mediapipe。请先安装 mediapipe==0.10.33，再运行 old.py。"
            )

        self.model_path = self._resolve_pose_model_path(model_path)
        self.backend = None
        self.mp_pose = None
        self.pose = None

        self._initialize_pose_backend()
        self.previous_landmarks = None
        self.previous_velocities = None

    def _resolve_pose_model_path(self, model_path=None):
        candidate_paths = []

        if model_path:
            candidate_paths.append(Path(model_path))

        env_model_path = os.getenv("MEDIAPIPE_POSE_TASK_PATH")
        if env_model_path:
            candidate_paths.append(Path(env_model_path))

        current_dir = Path(__file__).resolve().parent
        candidate_names = [
            "pose_landmarker_full.task",
            "pose_landmarker_heavy.task",
            "pose_landmarker_lite.task",
            "pose_landmarker.task",
            "models/pose_landmarker_full.task",
            "models/pose_landmarker_heavy.task",
            "models/pose_landmarker_lite.task",
            "saved_models/pose_landmarker_full.task",
            "saved_models/pose_landmarker_heavy.task",
            "saved_models/pose_landmarker_lite.task",
        ]

        for name in candidate_names:
            candidate_paths.append(current_dir / name)

        for candidate in candidate_paths:
            if candidate and candidate.exists() and candidate.is_file():
                return candidate

        return None

    def _initialize_pose_backend(self):
        tasks_ready = all([mp_python is not None, mp_vision is not None, self.model_path is not None])

        if tasks_ready:
            try:
                base_options = mp_python.BaseOptions(model_asset_path=str(self.model_path))
                options = mp_vision.PoseLandmarkerOptions(
                    base_options=base_options,
                    running_mode=mp_vision.RunningMode.IMAGE,
                    num_poses=1,
                    min_pose_detection_confidence=0.5,
                    min_pose_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                    output_segmentation_masks=False,
                )
                self.pose = mp_vision.PoseLandmarker.create_from_options(options)
                self.backend = "mediapipe_tasks"
                print(f"已使用 MediaPipe Tasks 姿态模型: {self.model_path}")
                return
            except Exception as e:
                print(f"MediaPipe Tasks 初始化失败，切换到兼容模式: {e}")

        if hasattr(mp, "solutions") and hasattr(mp.solutions, "pose"):
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.backend = "mediapipe_solutions"
            if self.model_path is None:
                print(
                    "未找到 pose_landmarker .task 模型，当前使用 MediaPipe Solutions 兼容模式。"
                    "如需完全切换到 0.10.33 新接口，请设置 MEDIAPIPE_POSE_TASK_PATH "
                    "或将 pose_landmarker_full.task 放到项目目录。"
                )
            return

        raise RuntimeError(
            "当前 mediapipe 环境不可用：既无法初始化 Tasks API，也不支持旧 Solutions API。"
        )

    def _extract_landmarks_with_tasks(self, frame_rgb):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        results = self.pose.detect(mp_image)

        if not results.pose_landmarks:
            return None

        landmarks = []
        for landmark in results.pose_landmarks[0]:
            visibility = getattr(landmark, "visibility", None)
            if visibility is None:
                visibility = getattr(landmark, "presence", 1.0)
            landmarks.extend([landmark.x, landmark.y, landmark.z, visibility])

        if len(landmarks) < 132:
            landmarks.extend([0.0] * (132 - len(landmarks)))

        return np.array(landmarks[:132], dtype=np.float32)

    def _extract_landmarks_with_solutions(self, frame_rgb):
        results = self.pose.process(frame_rgb)
        if not results.pose_landmarks:
            return None

        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])

        return np.array(landmarks, dtype=np.float32)

    def extract_landmarks_from_frame(self, frame):
        """从单帧提取关键点"""
        try:
            height, width = frame.shape[:2]
            # 电脑版本可以处理更大的图像
            if height > 720 or width > 1280:
                scale = min(720 / height, 1280 / width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.backend == "mediapipe_tasks":
                return self._extract_landmarks_with_tasks(frame_rgb)
            if self.backend == "mediapipe_solutions":
                return self._extract_landmarks_with_solutions(frame_rgb)
            return None
        except Exception as e:
            print(f"提取关键点时出错: {e}")
            return None

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def calculate_velocity(self, current_landmarks, previous_landmarks, time_delta=1 / 30.0):
        if previous_landmarks is None:
            return np.zeros(len(current_landmarks))
        velocity = (current_landmarks - previous_landmarks) / time_delta
        return velocity

    def calculate_acceleration(self, current_velocity, previous_velocity, time_delta=1 / 30.0):
        if previous_velocity is None:
            return np.zeros(len(current_velocity))
        acceleration = (current_velocity - previous_velocity) / time_delta
        return acceleration

    def extract_advanced_features_from_landmarks(self, landmarks_array):
        """从关键点提取高级特征"""
        if landmarks_array is None:
            return None

        if not isinstance(landmarks_array, np.ndarray):
            landmarks_array = np.array(landmarks_array)

        if landmarks_array.ndim == 1:
            if len(landmarks_array) >= 132:
                landmarks = landmarks_array[:132].reshape(-1, 4)
            else:
                padded = np.zeros(132)
                padded[:len(landmarks_array)] = landmarks_array
                landmarks = padded.reshape(-1, 4)
        else:
            landmarks = landmarks_array.reshape(-1, 4)

        features = []

        # 1. 归一化的坐标特征
        if len(landmarks) > 24:
            try:
                hip_center_x = (landmarks[23][0] + landmarks[24][0]) / 2
                hip_center_y = (landmarks[23][1] + landmarks[24][1]) / 2

                if len(landmarks) > 12:
                    body_scale = self.calculate_distance(landmarks[11][:2], landmarks[12][:2])
                    if body_scale < 0.01:
                        body_scale = 1.0
                else:
                    body_scale = 1.0

                for i in range(min(33, len(landmarks))):
                    norm_x = (landmarks[i][0] - hip_center_x) / body_scale
                    norm_y = (landmarks[i][1] - hip_center_y) / body_scale
                    norm_z = landmarks[i][2] / body_scale
                    features.extend([norm_x, norm_y, norm_z])
            except:
                for i in range(min(33, len(landmarks))):
                    features.extend([landmarks[i][0], landmarks[i][1], landmarks[i][2]])
        else:
            for i in range(min(33, len(landmarks))):
                if i < len(landmarks):
                    features.extend([landmarks[i][0], landmarks[i][1], landmarks[i][2]])
                else:
                    features.extend([0.0, 0.0, 0.0])

        while len(features) < 99:
            features.append(0.0)

        # 2. 角度特征
        angles = []
        try:
            for side in ['left', 'right']:
                if side == 'left':
                    shoulder_idx, elbow_idx, wrist_idx = 11, 13, 15
                else:
                    shoulder_idx, elbow_idx, wrist_idx = 12, 14, 16

                if len(landmarks) > max(shoulder_idx, elbow_idx, wrist_idx):
                    shoulder = landmarks[shoulder_idx][:2]
                    elbow = landmarks[elbow_idx][:2]
                    wrist = landmarks[wrist_idx][:2]
                    angles.append(self.calculate_angle(shoulder, elbow, wrist))
                else:
                    angles.append(0.0)

            for side in ['left', 'right']:
                if side == 'left':
                    hip_idx, knee_idx, ankle_idx = 23, 25, 27
                else:
                    hip_idx, knee_idx, ankle_idx = 24, 26, 28

                if len(landmarks) > max(hip_idx, knee_idx, ankle_idx):
                    hip = landmarks[hip_idx][:2]
                    knee = landmarks[knee_idx][:2]
                    ankle = landmarks[ankle_idx][:2]
                    angles.append(self.calculate_angle(hip, knee, ankle))
                else:
                    angles.append(0.0)

            if len(landmarks) > 28:
                shoulder_center = [(landmarks[11][0] + landmarks[12][0]) / 2,
                                   (landmarks[11][1] + landmarks[12][1]) / 2]
                hip_center = [(landmarks[23][0] + landmarks[24][0]) / 2,
                              (landmarks[23][1] + landmarks[24][1]) / 2]
                knee_center = [(landmarks[25][0] + landmarks[26][0]) / 2,
                               (landmarks[25][1] + landmarks[26][1]) / 2]
                angles.append(self.calculate_angle(shoulder_center, hip_center, knee_center))

                if len(landmarks) > 0:
                    head = landmarks[0][:2]
                    angles.append(self.calculate_angle(head, shoulder_center, hip_center))
                else:
                    angles.append(0.0)
            else:
                angles.extend([0.0, 0.0])

        except Exception as e:
            angles = [0.0] * 6

        features.extend(angles)

        # 3. 距离特征
        distances = []
        try:
            if len(landmarks) > 16:
                distances.append(self.calculate_distance(landmarks[15][:2], landmarks[16][:2]))
            else:
                distances.append(0.0)

            if len(landmarks) > 28:
                distances.append(self.calculate_distance(landmarks[27][:2], landmarks[28][:2]))
                distances.append(self.calculate_distance(landmarks[11][:2], landmarks[12][:2]))
                distances.append(self.calculate_distance(landmarks[23][:2], landmarks[24][:2]))

                shoulder_center = [(landmarks[11][0] + landmarks[12][0]) / 2,
                                   (landmarks[11][1] + landmarks[12][1]) / 2]
                hip_center = [(landmarks[23][0] + landmarks[24][0]) / 2,
                              (landmarks[23][1] + landmarks[24][1]) / 2]
                distances.append(self.calculate_distance(shoulder_center, hip_center))

                distances.append(self.calculate_distance(landmarks[15][:2], landmarks[23][:2]))
                distances.append(self.calculate_distance(landmarks[16][:2], landmarks[24][:2]))
            else:
                distances.extend([0.0] * 6)

        except Exception as e:
            distances = [0.0] * 7

        features.extend(distances)

        # 4. 速度特征
        current_landmarks_flat = landmarks_array.flatten() if landmarks_array.ndim > 1 else landmarks_array
        if self.previous_landmarks is not None:
            velocity = self.calculate_velocity(current_landmarks_flat, self.previous_landmarks)
            key_velocities = []
            for idx in [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]:
                if idx * 4 + 3 < len(velocity):
                    key_velocities.extend([velocity[idx * 4], velocity[idx * 4 + 1]])
                else:
                    key_velocities.extend([0.0, 0.0])
            features.extend(key_velocities[:26])
        else:
            features.extend([0.0] * 26)

        # 5. 加速度特征
        if self.previous_velocities is not None and self.previous_landmarks is not None:
            current_velocity = self.calculate_velocity(current_landmarks_flat, self.previous_landmarks)
            acceleration = self.calculate_acceleration(current_velocity, self.previous_velocities)
            key_accelerations = []
            for idx in [0, 11, 12, 15, 16, 23, 24, 27, 28]:
                if idx * 4 + 3 < len(acceleration):
                    key_accelerations.extend([acceleration[idx * 4], acceleration[idx * 4 + 1]])
                else:
                    key_accelerations.extend([0.0, 0.0])
            features.extend(key_accelerations[:18])
            self.previous_velocities = current_velocity
        else:
            features.extend([0.0] * 18)
            if self.previous_landmarks is not None:
                self.previous_velocities = self.calculate_velocity(current_landmarks_flat, self.previous_landmarks)

        self.previous_landmarks = current_landmarks_flat.copy()

        # 6. 对称性特征
        symmetry_features = []
        try:
            if len(landmarks) > 16:
                left_arm_len = self.calculate_distance(landmarks[11][:2], landmarks[15][:2])
                right_arm_len = self.calculate_distance(landmarks[12][:2], landmarks[16][:2])
                symmetry_features.append(abs(left_arm_len - right_arm_len))
            else:
                symmetry_features.append(0.0)

            if len(landmarks) > 28:
                left_leg_len = self.calculate_distance(landmarks[23][:2], landmarks[27][:2])
                right_leg_len = self.calculate_distance(landmarks[24][:2], landmarks[28][:2])
                symmetry_features.append(abs(left_leg_len - right_leg_len))
            else:
                symmetry_features.append(0.0)

        except:
            symmetry_features = [0.0, 0.0]

        features.extend(symmetry_features)

        return np.array(features)


class ExerciseCounterOptimized:
    """优化版动作计数器（含卡路里计算）"""

    def __init__(self, target_exercises, user_profile, calorie_calculator):
        self.target_exercises = target_exercises
        self.user_profile = user_profile
        self.calorie_calculator = calorie_calculator
        self.counts = {exercise: 0 for exercise in target_exercises}
        self.calories = {exercise: 0.0 for exercise in target_exercises}
        self.last_predictions = deque(maxlen=10)
        self.exercise_states = {exercise: 'none' for exercise in target_exercises}
        self.position_trackers = {exercise: deque(maxlen=20) for exercise in target_exercises}
        self.confidence_threshold = 0.7
        self.state_change_threshold = 5

        self.rep_start_times = {exercise: None for exercise in target_exercises}
        self.rep_durations = {exercise: deque(maxlen=10) for exercise in target_exercises}

        self.exercise_specific_data = {
            exercise: {
                'last_key_angle': None,
                'last_key_height': None,
                'min_angle_seen': float('inf'),
                'max_angle_seen': 0,
                'min_height_seen': float('inf'),
                'max_height_seen': 0,
                'stable_frames': 0,
                'transition_frames': 0
            } for exercise in target_exercises
        }

        self.exercise_configs = {
            'barbell biceps curl': {
                'key_joints': [13, 14, 15, 16],
                'angle_joints': [(11, 13, 15), (12, 14, 16)],
                'count_on_angle_change': True,
                'angle_threshold': 30,
                'min_angle': 70,
                'max_angle': 160
            },
            'hammer curl': {
                'key_joints': [13, 14, 15, 16],
                'angle_joints': [(11, 13, 15), (12, 14, 16)],
                'count_on_angle_change': True,
                'angle_threshold': 20,
                'min_angle': 60,
                'max_angle': 170,
                'stable_frames_required': 1,
                'transition_frames_required': 2,
                'enhanced_detection': True
            },
            'push-up': {
                'key_joints': [11, 12, 13, 14, 15, 16],
                'angle_joints': [(11, 13, 15), (12, 14, 16)],
                'count_on_angle_change': True,
                'angle_threshold': 20,
                'min_angle': 70,
                'max_angle': 140,
                'stable_frames_required': 2,
                'transition_frames_required': 3,
                'use_enhanced_detection': True
            },
            'shoulder press': {
                'key_joints': [11, 12, 13, 14, 15, 16],
                'angle_joints': [(11, 13, 15), (12, 14, 16)],
                'count_on_angle_change': True,
                'angle_threshold': 30,
                'min_angle': 60,
                'max_angle': 160
            },
            'squat': {
                'key_joints': [23, 24, 25, 26, 27, 28],
                'angle_joints': [(23, 25, 27), (24, 26, 28)],
                'count_on_angle_change': True,
                'angle_threshold': 40,
                'min_angle': 70,
                'max_angle': 170
            }
        }

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def smooth_angle_sequence(self, angles, window_size=5):
        if len(angles) < window_size:
            return angles[-1] if angles else 0
        recent_angles = list(angles)[-window_size:]
        return np.mean(recent_angles)

    def start_rep_timer(self, exercise):
        self.rep_start_times[exercise] = time.time()

    def end_rep_timer_and_calculate_calories(self, exercise):
        if self.rep_start_times[exercise] is None:
            rep_duration_sec = self.calorie_calculator.estimate_rep_duration(exercise)
        else:
            rep_duration_sec = time.time() - self.rep_start_times[exercise]
            self.rep_start_times[exercise] = None

        self.rep_durations[exercise].append(rep_duration_sec)

        rep_duration_min = rep_duration_sec / 60.0
        added_weight = self.user_profile.added_weights.get(exercise, 0)

        calories_burned = self.calorie_calculator.calculate_calories_per_rep(
            exercise,
            self.user_profile.body_weight,
            self.user_profile.age,
            self.user_profile.gender,
            rep_duration_min,
            added_weight
        )

        self.calories[exercise] += calories_burned
        return calories_burned

    def detect_rep_completion(self, exercise, landmarks):
        """检测重复完成"""
        if exercise not in self.exercise_configs:
            return False

        if exercise == 'push-up':
            return self._detect_pushup_rep_enhanced(exercise, landmarks)

        if exercise == 'hammer curl':
            return self._detect_hammer_curl_rep_enhanced(exercise, landmarks)

        config = self.exercise_configs[exercise]
        return self._detect_angle_based_rep_improved(exercise, landmarks, config)

    def _detect_hammer_curl_rep_enhanced(self, exercise, landmarks):
        """增强版hammer curl检测"""
        if len(landmarks) < 132:
            return False

        landmarks_reshaped = landmarks[:132].reshape(-1, 4)
        config = self.exercise_configs[exercise]

        angles = []
        left_angle = right_angle = None

        if all(idx < len(landmarks_reshaped) for idx in [11, 13, 15]):
            left_shoulder = landmarks_reshaped[11][:2]
            left_elbow = landmarks_reshaped[13][:2]
            left_wrist = landmarks_reshaped[15][:2]

            if (np.linalg.norm(np.array(left_shoulder) - np.array(left_elbow)) > 0.01 and
                    np.linalg.norm(np.array(left_elbow) - np.array(left_wrist)) > 0.01):
                left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                angles.append(left_angle)

        if all(idx < len(landmarks_reshaped) for idx in [12, 14, 16]):
            right_shoulder = landmarks_reshaped[12][:2]
            right_elbow = landmarks_reshaped[14][:2]
            right_wrist = landmarks_reshaped[16][:2]

            if (np.linalg.norm(np.array(right_shoulder) - np.array(right_elbow)) > 0.01 and
                    np.linalg.norm(np.array(right_elbow) - np.array(right_wrist)) > 0.01):
                right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                angles.append(right_angle)

        if not angles:
            return False

        if len(angles) == 2:
            left_var = abs(left_angle - self.exercise_specific_data[exercise].get('last_left_angle', left_angle))
            right_var = abs(right_angle - self.exercise_specific_data[exercise].get('last_right_angle', right_angle))

            if left_var >= right_var:
                current_angle = left_angle
                self.exercise_specific_data[exercise]['primary_arm'] = 'left'
            else:
                current_angle = right_angle
                self.exercise_specific_data[exercise]['primary_arm'] = 'right'

            self.exercise_specific_data[exercise]['last_left_angle'] = left_angle
            self.exercise_specific_data[exercise]['last_right_angle'] = right_angle
        else:
            current_angle = angles[0]

        self.position_trackers[exercise].append(current_angle)

        if len(self.position_trackers[exercise]) < 6:
            return False

        data = self.exercise_specific_data[exercise]
        smoothed_angle = self.smooth_angle_sequence(self.position_trackers[exercise], window_size=3)

        data['min_angle_seen'] = min(data['min_angle_seen'], smoothed_angle)
        data['max_angle_seen'] = max(data['max_angle_seen'], smoothed_angle)

        angle_range = data['max_angle_seen'] - data['min_angle_seen']
        if angle_range > 25:
            dynamic_max_threshold = data['min_angle_seen'] + angle_range * 0.75
            dynamic_min_threshold = data['min_angle_seen'] + angle_range * 0.35
        else:
            dynamic_max_threshold = config['max_angle']
            dynamic_min_threshold = config['min_angle']

        angle_velocity = 0
        if len(self.position_trackers[exercise]) >= 3:
            recent_angles = list(self.position_trackers[exercise])[-3:]
            angle_velocity = recent_angles[-1] - recent_angles[-3]

        return self._detect_hammer_curl_with_velocity(exercise, smoothed_angle, angle_velocity,
                                                      dynamic_max_threshold, dynamic_min_threshold)

    def _detect_hammer_curl_with_velocity(self, exercise, angle, angle_velocity, max_threshold, min_threshold):
        """带速度检测的hammer curl识别"""
        current_state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]

        stability_margin = 8
        velocity_threshold = 1.5

        if current_state == 'none':
            if angle > max_threshold - 15:
                self.exercise_states[exercise] = 'extended'
                data['stable_frames'] = 0
                self.start_rep_timer(exercise)
                return False

        elif current_state == 'extended':
            if angle > max_threshold - stability_margin:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = max(0, data['stable_frames'] - 1)

            if (angle < max_threshold - 12 and
                    angle_velocity < -velocity_threshold):
                self.exercise_states[exercise] = 'flexing'
                data['transition_frames'] = 0
                return False

        elif current_state == 'flexing':
            data['transition_frames'] += 1

            if angle > max_threshold - 10 and angle_velocity > velocity_threshold:
                self.exercise_states[exercise] = 'extended'
                return False

            if (angle < min_threshold + 15 and
                    data['transition_frames'] >= 2):
                self.exercise_states[exercise] = 'flexed'
                data['stable_frames'] = 0
                return False

        elif current_state == 'flexed':
            if angle < min_threshold + stability_margin:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = max(0, data['stable_frames'] - 1)

            if (angle > min_threshold + 12 and
                    angle_velocity > velocity_threshold):
                self.exercise_states[exercise] = 'extending'
                data['transition_frames'] = 0
                return False

        elif current_state == 'extending':
            data['transition_frames'] += 1

            if angle < min_threshold + 10 and angle_velocity < -velocity_threshold:
                self.exercise_states[exercise] = 'flexed'
                return False

            if (angle > max_threshold - 15 and
                    data['transition_frames'] >= 2):
                self.exercise_states[exercise] = 'extended'
                data['stable_frames'] = 0
                return True

        return False

    def _detect_angle_based_rep_improved(self, exercise, landmarks, config):
        """改进的基于角度变化的动作检测"""
        if len(landmarks) < 132:
            return False

        landmarks_reshaped = landmarks[:132].reshape(-1, 4)

        angles = []
        for angle_joints in config['angle_joints']:
            if all(idx < len(landmarks_reshaped) for idx in angle_joints):
                a = landmarks_reshaped[angle_joints[0]][:2]
                b = landmarks_reshaped[angle_joints[1]][:2]
                c = landmarks_reshaped[angle_joints[2]][:2]

                if (np.linalg.norm(np.array(a) - np.array(b)) > 0.01 and
                        np.linalg.norm(np.array(b) - np.array(c)) > 0.01):
                    angle = self.calculate_angle(a, b, c)
                    angles.append(angle)

        if not angles:
            return False

        current_angle = np.mean(angles)
        self.position_trackers[exercise].append(current_angle)

        if len(self.position_trackers[exercise]) < 10:
            return False

        data = self.exercise_specific_data[exercise]
        smoothed_angle = self.smooth_angle_sequence(self.position_trackers[exercise])

        data['min_angle_seen'] = min(data['min_angle_seen'], smoothed_angle)
        data['max_angle_seen'] = max(data['max_angle_seen'], smoothed_angle)

        if data['max_angle_seen'] - data['min_angle_seen'] > 40:
            dynamic_max_threshold = data['min_angle_seen'] + (data['max_angle_seen'] - data['min_angle_seen']) * 0.8
            dynamic_min_threshold = data['min_angle_seen'] + (data['max_angle_seen'] - data['min_angle_seen']) * 0.3
        else:
            dynamic_max_threshold = config['max_angle']
            dynamic_min_threshold = config['min_angle']

        rep_completed = False

        if exercise in ['barbell biceps curl']:
            rep_completed = self._detect_curl_rep(exercise, smoothed_angle, dynamic_max_threshold,
                                                  dynamic_min_threshold)
        elif exercise == 'push-up':
            rep_completed = self._detect_pushup_rep(exercise, smoothed_angle, dynamic_max_threshold,
                                                    dynamic_min_threshold)
        elif exercise == 'shoulder press':
            rep_completed = self._detect_shoulder_press_rep(exercise, smoothed_angle, dynamic_max_threshold,
                                                            dynamic_min_threshold)
        elif exercise == 'squat':
            rep_completed = self._detect_squat_rep(exercise, smoothed_angle, dynamic_max_threshold,
                                                   dynamic_min_threshold)

        return rep_completed

    def _detect_curl_rep(self, exercise, angle, max_threshold, min_threshold):
        current_state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]

        if current_state == 'none':
            if angle > max_threshold - 10:
                self.exercise_states[exercise] = 'extended'
                data['stable_frames'] = 0
                self.start_rep_timer(exercise)
        elif current_state == 'extended':
            if angle > max_threshold - 10:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle < min_threshold + 20:
                self.exercise_states[exercise] = 'flexing'
                data['transition_frames'] = 0
        elif current_state == 'flexing':
            data['transition_frames'] += 1
            if angle < min_threshold + 10:
                self.exercise_states[exercise] = 'flexed'
                data['stable_frames'] = 0
        elif current_state == 'flexed':
            if angle < min_threshold + 15:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle > max_threshold - 20:
                self.exercise_states[exercise] = 'extending'
                data['transition_frames'] = 0
        elif current_state == 'extending':
            data['transition_frames'] += 1
            if angle > max_threshold - 10:
                self.exercise_states[exercise] = 'extended'
                return True

        return False

    def _detect_pushup_rep_enhanced(self, exercise, landmarks):
        """增强版俯卧撑检测"""
        if len(landmarks) < 132:
            return False

        landmarks_reshaped = landmarks[:132].reshape(-1, 4)

        config = self.exercise_configs[exercise]
        angles = []
        for angle_joints in config['angle_joints']:
            if all(idx < len(landmarks_reshaped) for idx in angle_joints):
                a = landmarks_reshaped[angle_joints[0]][:2]
                b = landmarks_reshaped[angle_joints[1]][:2]
                c = landmarks_reshaped[angle_joints[2]][:2]

                if (np.linalg.norm(np.array(a) - np.array(b)) > 0.01 and
                        np.linalg.norm(np.array(b) - np.array(c)) > 0.01):
                    angle = self.calculate_angle(a, b, c)
                    angles.append(angle)

        if not angles:
            return False

        arm_angle = np.mean(angles)

        try:
            shoulder_center_y = (landmarks_reshaped[11][1] + landmarks_reshaped[12][1]) / 2
            wrist_center_y = (landmarks_reshaped[15][1] + landmarks_reshaped[16][1]) / 2
            body_height = abs(shoulder_center_y - wrist_center_y)

            hip_center_y = (landmarks_reshaped[23][1] + landmarks_reshaped[24][1]) / 2
            torso_angle = abs(shoulder_center_y - hip_center_y)

        except:
            body_height = 0
            torso_angle = 0

        normalized_height = min(180, max(0, body_height * 1000))
        combined_score = arm_angle * 0.7 + normalized_height * 0.3

        self.position_trackers[exercise].append(combined_score)

        if len(self.position_trackers[exercise]) < 10:
            return False

        data = self.exercise_specific_data[exercise]
        smoothed_score = self.smooth_angle_sequence(self.position_trackers[exercise])

        data['min_angle_seen'] = min(data['min_angle_seen'], smoothed_score)
        data['max_angle_seen'] = max(data['max_angle_seen'], smoothed_score)

        if data['max_angle_seen'] - data['min_angle_seen'] > 30:
            dynamic_max_threshold = data['min_angle_seen'] + (data['max_angle_seen'] - data['min_angle_seen']) * 0.75
            dynamic_min_threshold = data['min_angle_seen'] + (data['max_angle_seen'] - data['min_angle_seen']) * 0.35
        else:
            dynamic_max_threshold = 120
            dynamic_min_threshold = 80

        return self._detect_pushup_rep_improved(exercise, smoothed_score, dynamic_max_threshold, dynamic_min_threshold)

    def _detect_pushup_rep_improved(self, exercise, score, max_threshold, min_threshold):
        current_state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]

        recent_scores = list(self.position_trackers[exercise])[-10:]
        if len(recent_scores) < 5:
            return False

        score_velocity = 0
        if len(recent_scores) >= 3:
            score_velocity = recent_scores[-1] - recent_scores[-3]

        if current_state == 'none':
            if score > max_threshold - 10:
                self.exercise_states[exercise] = 'up'
                data['stable_frames'] = 0
                data['transition_frames'] = 0
                self.start_rep_timer(exercise)

        elif current_state == 'up':
            if score > max_threshold - 15:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = max(0, data['stable_frames'] - 1)

            if (data['stable_frames'] >= 2 and
                    score < max_threshold - 20 and
                    score_velocity < -2):
                self.exercise_states[exercise] = 'going_down'
                data['transition_frames'] = 0
                data['stable_frames'] = 0

        elif current_state == 'going_down':
            data['transition_frames'] += 1

            if score > max_threshold - 15 and score_velocity > 1:
                self.exercise_states[exercise] = 'up'
                data['stable_frames'] = 0
                return False

            if (score < min_threshold + 25 and
                    data['transition_frames'] >= 3):
                self.exercise_states[exercise] = 'down'
                data['stable_frames'] = 0
                data['transition_frames'] = 0

        elif current_state == 'down':
            if score < min_threshold + 30:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = max(0, data['stable_frames'] - 1)

            if (data['stable_frames'] >= 2 and
                    score > min_threshold + 35 and
                    score_velocity > 2):
                self.exercise_states[exercise] = 'going_up'
                data['transition_frames'] = 0
                data['stable_frames'] = 0

        elif current_state == 'going_up':
            data['transition_frames'] += 1

            if score < min_threshold + 30 and score_velocity < -1:
                self.exercise_states[exercise] = 'down'
                data['stable_frames'] = 0
                return False

            if (score > max_threshold - 15 and
                    data['transition_frames'] >= 3):
                self.exercise_states[exercise] = 'up'
                data['stable_frames'] = 0
                data['transition_frames'] = 0
                return True

        return False

    def _detect_shoulder_press_rep(self, exercise, angle, max_threshold, min_threshold):
        current_state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]

        if current_state == 'none':
            if angle < min_threshold + 20:
                self.exercise_states[exercise] = 'down'
                data['stable_frames'] = 0
                self.start_rep_timer(exercise)
        elif current_state == 'down':
            if angle < min_threshold + 25:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle > min_threshold + 40:
                self.exercise_states[exercise] = 'pressing_up'
                data['transition_frames'] = 0
        elif current_state == 'pressing_up':
            data['transition_frames'] += 1
            if angle > max_threshold - 20:
                self.exercise_states[exercise] = 'up'
                data['stable_frames'] = 0
        elif current_state == 'up':
            if angle > max_threshold - 25:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle < max_threshold - 40:
                self.exercise_states[exercise] = 'pressing_down'
                data['transition_frames'] = 0
        elif current_state == 'pressing_down':
            data['transition_frames'] += 1
            if angle < min_threshold + 20:
                self.exercise_states[exercise] = 'down'
                return True

        return False

    def _detect_squat_rep(self, exercise, angle, max_threshold, min_threshold):
        current_state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]

        if current_state == 'none':
            if angle > max_threshold - 10:
                self.exercise_states[exercise] = 'standing'
                data['stable_frames'] = 0
                self.start_rep_timer(exercise)
        elif current_state == 'standing':
            if angle > max_threshold - 15:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle < max_threshold - 30:
                self.exercise_states[exercise] = 'squatting_down'
                data['transition_frames'] = 0
        elif current_state == 'squatting_down':
            data['transition_frames'] += 1
            if angle < min_threshold + 20:
                self.exercise_states[exercise] = 'squatting'
                data['stable_frames'] = 0
        elif current_state == 'squatting':
            if angle < min_threshold + 25:
                data['stable_frames'] += 1
            else:
                data['stable_frames'] = 0
            if angle > min_threshold + 40:
                self.exercise_states[exercise] = 'standing_up'
                data['transition_frames'] = 0
        elif current_state == 'standing_up':
            data['transition_frames'] += 1
            if angle > max_threshold - 10:
                self.exercise_states[exercise] = 'standing'
                return True

        return False

    def update_counts(self, predicted_exercise, confidence, landmarks):
        if confidence < self.confidence_threshold:
            return

        if predicted_exercise in self.target_exercises:
            if self.detect_rep_completion(predicted_exercise, landmarks):
                self.counts[predicted_exercise] += 1
                calories_burned = self.end_rep_timer_and_calculate_calories(predicted_exercise)
                print(f"{predicted_exercise}: {self.counts[predicted_exercise]} 次 "
                      f"(+{calories_burned:.2f} 卡路里)")

    def get_counts(self):
        return self.counts.copy()

    def get_calories(self):
        return self.calories.copy()

    def get_total_calories(self):
        return sum(self.calories.values())

    def reset_counts(self):
        self.counts = {exercise: 0 for exercise in self.target_exercises}
        self.calories = {exercise: 0.0 for exercise in self.target_exercises}
        self.exercise_states = {exercise: 'none' for exercise in self.target_exercises}
        for tracker in self.position_trackers.values():
            tracker.clear()

        self.rep_start_times = {exercise: None for exercise in self.target_exercises}
        for durations in self.rep_durations.values():
            durations.clear()

        for exercise in self.target_exercises:
            self.exercise_specific_data[exercise] = {
                'last_key_angle': None,
                'last_key_height': None,
                'min_angle_seen': float('inf'),
                'max_angle_seen': 0,
                'min_height_seen': float('inf'),
                'max_height_seen': 0,
                'stable_frames': 0,
                'transition_frames': 0
            }

    def get_exercise_info(self, exercise):
        if exercise not in self.target_exercises:
            return None

        state = self.exercise_states[exercise]
        data = self.exercise_specific_data[exercise]
        recent_values = list(self.position_trackers[exercise])[-5:] if self.position_trackers[exercise] else []

        avg_duration = 0
        if self.rep_durations[exercise]:
            avg_duration = np.mean(list(self.rep_durations[exercise]))

        base_info = {
            'state': state,
            'min_angle_seen': data['min_angle_seen'],
            'max_angle_seen': data['max_angle_seen'],
            'stable_frames': data['stable_frames'],
            'transition_frames': data['transition_frames'],
            'recent_angles': recent_values,
            'current_angle': recent_values[-1] if recent_values else None,
            'avg_rep_duration': avg_duration,
            'calories_per_rep': 0
        }

        if avg_duration > 0:
            added_weight = self.user_profile.added_weights.get(exercise, 0)
            estimated_calories = self.calorie_calculator.calculate_calories_per_rep(
                exercise,
                self.user_profile.body_weight,
                self.user_profile.age,
                self.user_profile.gender,
                avg_duration / 60.0,
                added_weight
            )
            base_info['calories_per_rep'] = estimated_calories

        if exercise == 'hammer curl' and len(recent_values) >= 3:
            angle_velocity = recent_values[-1] - recent_values[-3]
            base_info.update({
                'angle_velocity': angle_velocity,
                'detection_type': 'enhanced_hammer_curl',
                'recent_angles': recent_values,
                'primary_arm': data.get('primary_arm', 'unknown')
            })

        if exercise == 'push-up' and len(recent_values) >= 3:
            score_velocity = recent_values[-1] - recent_values[-3]
            base_info.update({
                'score_velocity': score_velocity,
                'detection_type': 'enhanced_pushup',
                'recent_scores': recent_values
            })

        return base_info


class ExerciseRecognitionSystemPC:
    """电脑端健身动作识别系统"""

    def __init__(self, model_dir=None):
        if model_dir is None:
            possible_paths = [
                "./models",
                "./saved_models",
                "../models",
                "models"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    model_dir = path
                    break
            else:
                model_dir = "./models"

        self.model_dir = Path(model_dir)

        # 检测可用设备
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            print(f"使用设备: CUDA GPU")
        else:
            self.device = torch.device('cpu')
            print(f"使用设备: CPU")

        self.onnx_session = None
        self.input_name = None
        self.output_name = None

        self.label_encoder = None
        self.scaler = None
        self.feature_extractor = RealtimeFeatureExtractor()
        self.sequence_length = 30
        self.feature_buffer = deque(maxlen=self.sequence_length)

        self.target_exercises = [
            'barbell biceps curl', 'hammer curl', 'push-up',
            'shoulder press', 'squat'
        ]

        self.user_profile = UserProfile()
        self.calorie_calculator = CalorieCalculator()

        self.counter = None
        self.debug_mode = False
        self.simulation_mode = True

        try:
            self.load_onnx_model()
        except Exception as e:
            print(f"ONNX模型加载失败，启用模拟模式: {e}")
            self.simulation_mode = True

    def initialize_system(self):
        if not self.user_profile.profile_loaded:
            self.user_profile.load_from_input()

        self.counter = ExerciseCounterOptimized(
            self.target_exercises,
            self.user_profile,
            self.calorie_calculator
        )

    def load_onnx_model(self):
        """加载ONNX模型"""
        try:
            params_path = self.model_dir / "model_params.json"
            if not params_path.exists():
                raise FileNotFoundError("模型参数文件不存在")

            with open(params_path, 'r') as f:
                model_params = json.load(f)

            onnx_model_path = self.model_dir / "exercise_classifier.onnx"
            if not onnx_model_path.exists():
                raise FileNotFoundError("ONNX模型文件不存在")

            # 根据可用硬件选择提供者
            providers = []
            if torch.cuda.is_available():
                providers.append('CUDAExecutionProvider')
            providers.append('CPUExecutionProvider')

            self.onnx_session = ort.InferenceSession(
                str(onnx_model_path),
                providers=providers
            )

            self.input_name = self.onnx_session.get_inputs()[0].name
            self.output_name = self.onnx_session.get_outputs()[0].name

            encoder_path = self.model_dir / "label_encoder.pkl"
            if not encoder_path.exists():
                raise FileNotFoundError("标签编码器文件不存在")

            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)

            scaler_path = self.model_dir / "scaler.pkl"
            if not scaler_path.exists():
                raise FileNotFoundError("标准化器文件不存在")

            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            self.sequence_length = model_params.get('sequence_length', 30)
            self.feature_buffer = deque(maxlen=self.sequence_length)
            self.simulation_mode = False

            print("ONNX模型加载成功！")
            print(f"支持的动作类型: {list(self.label_encoder.classes_)}")
            print(f"推理提供者: {self.onnx_session.get_providers()}")

        except Exception as e:
            print(f"ONNX模型加载失败: {e}")
            raise

    def predict_exercise_simulation(self, landmarks):
        """模拟预测模式"""
        if landmarks is None:
            return None, 0.0

        try:
            landmarks_reshaped = landmarks[:132].reshape(-1, 4)

            left_shoulder = landmarks_reshaped[11][:2]
            left_elbow = landmarks_reshaped[13][:2]
            left_wrist = landmarks_reshaped[15][:2]
            left_angle = self.counter.calculate_angle(left_shoulder, left_elbow, left_wrist)

            right_shoulder = landmarks_reshaped[12][:2]
            right_elbow = landmarks_reshaped[14][:2]
            right_wrist = landmarks_reshaped[16][:2]
            right_angle = self.counter.calculate_angle(right_shoulder, right_elbow, right_wrist)

            avg_arm_angle = (left_angle + right_angle) / 2

            left_wrist_y = landmarks_reshaped[15][1]
            right_wrist_y = landmarks_reshaped[16][1]
            shoulder_y = (landmarks_reshaped[11][1] + landmarks_reshaped[12][1]) / 2

            if left_wrist_y < shoulder_y and right_wrist_y < shoulder_y:
                if avg_arm_angle > 120:
                    return 'shoulder press', 0.8
                else:
                    return 'push-up', 0.8
            elif avg_arm_angle < 100:
                return 'barbell biceps curl', 0.8
            else:
                return 'squat', 0.8

        except Exception as e:
            return None, 0.0

    def predict_exercise(self, frame):
        """预测当前帧的动作"""
        landmarks = self.feature_extractor.extract_landmarks_from_frame(frame)
        if landmarks is None:
            return None, 0.0, landmarks

        if self.simulation_mode:
            predicted_exercise, confidence = self.predict_exercise_simulation(landmarks)
            return predicted_exercise, confidence, landmarks

        features = self.feature_extractor.extract_advanced_features_from_landmarks(landmarks)
        if features is None:
            return None, 0.0, landmarks

        self.feature_buffer.append(features)

        if len(self.feature_buffer) < self.sequence_length:
            return None, 0.0, landmarks

        sequence = np.array(list(self.feature_buffer))

        original_shape = sequence.shape
        sequence_2d = sequence.reshape(-1, sequence.shape[-1])
        sequence_scaled = self.scaler.transform(sequence_2d)
        sequence_scaled = sequence_scaled.reshape(original_shape)

        try:
            input_data = sequence_scaled.astype(np.float32)
            input_data = np.expand_dims(input_data, axis=0)

            outputs = self.onnx_session.run([self.output_name], {self.input_name: input_data})
            output = outputs[0]

            exp_output = np.exp(output - np.max(output, axis=1, keepdims=True))
            probabilities = exp_output / np.sum(exp_output, axis=1, keepdims=True)

            predicted_class = np.argmax(probabilities, axis=1)[0]
            confidence_value = probabilities[0][predicted_class]

            predicted_exercise = self.label_encoder.classes_[predicted_class]

            return predicted_exercise, confidence_value, landmarks

        except Exception as e:
            print(f"ONNX推理错误: {e}")
            return None, 0.0, landmarks

    def get_runtime_stats(self, predicted_exercise=None, confidence=0.0):
        if self.counter is None:
            return {
                "exercise": predicted_exercise,
                "confidence": float(confidence),
                "counts": {},
                "calories": {},
                "total_reps": 0,
                "total_calories": 0.0,
            }

        counts = self.counter.get_counts()
        calories = self.counter.get_calories()
        return {
            "exercise": predicted_exercise,
            "confidence": float(confidence),
            "counts": counts,
            "calories": calories,
            "total_reps": int(sum(counts.values())),
            "total_calories": float(self.counter.get_total_calories()),
        }

    def render_realtime_frame(self, frame, fps=0):
        """处理一帧并输出和电脑端页面一致的叠加画面"""
        if self.counter is None:
            self.initialize_system()

        predicted_exercise, confidence, landmarks = self.predict_exercise(frame)
        display_frame = frame.copy()
        display_frame = self.draw_pose_landmarks(display_frame, landmarks)

        if predicted_exercise and predicted_exercise in self.target_exercises and landmarks is not None:
            self.counter.update_counts(predicted_exercise, confidence, landmarks)

        self._draw_info_panel(display_frame, predicted_exercise, confidence, fps)
        stats = self.get_runtime_stats(predicted_exercise, confidence)
        return display_frame, stats, landmarks

    def draw_pose_landmarks(self, frame, landmarks):
        """绘制姿态关键点"""
        if landmarks is None or len(landmarks) < 132:
            return frame

        landmarks_reshaped = landmarks[:132].reshape(-1, 4)
        height, width = frame.shape[:2]

        connections = [
            (11, 12), (11, 23), (12, 24), (23, 24),
            (11, 13), (13, 15),
            (12, 14), (14, 16),
            (23, 25), (25, 27),
            (24, 26), (26, 28),
        ]

        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(landmarks_reshaped) and end_idx < len(landmarks_reshaped):
                start_point = landmarks_reshaped[start_idx]
                end_point = landmarks_reshaped[end_idx]

                if start_point[3] > 0.5 and end_point[3] > 0.5:
                    start_x = int(start_point[0] * width)
                    start_y = int(start_point[1] * height)
                    end_x = int(end_point[0] * width)
                    end_y = int(end_point[1] * height)

                    if (0 <= start_x < width and 0 <= start_y < height and
                            0 <= end_x < width and 0 <= end_y < height):
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 3)

        key_points = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

        for idx in key_points:
            if idx < len(landmarks_reshaped):
                point = landmarks_reshaped[idx]
                if point[3] > 0.5:
                    x = int(point[0] * width)
                    y = int(point[1] * height)

                    if 0 <= x < width and 0 <= y < height:
                        cv2.circle(frame, (x, y), 6, (0, 0, 255), -1)
                        cv2.circle(frame, (x, y), 6, (255, 255, 255), 2)

        return frame

    def _draw_info_panel(self, frame, predicted_exercise, confidence, fps):
        """绘制信息面板"""
        height, width = frame.shape[:2]

        panel_width = min(320, width // 4)
        panel_x = width - panel_width - 10

        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, 10), (width - 10, 480), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        cv2.rectangle(frame, (panel_x, 10), (width - 10, 480), (255, 255, 255), 3)

        font_scale_title = 0.7
        font_scale_normal = 0.6
        font_scale_small = 0.5
        thickness_title = 2
        thickness_normal = 2
        thickness_small = 1
        line_height = 25

        y_pos = 40

        mode_text = "Exercise Recognition"
        if self.simulation_mode:
            mode_text += " (Sim)"
        draw_text_enhanced(frame, mode_text, (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_title, (0, 255, 255), thickness_title)
        y_pos += 30

        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 20

        if predicted_exercise:
            exercise_text = f"Exercise: {predicted_exercise[:13]}..."
            confidence_text = f"Confidence: {confidence:.2f}"
            color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)
        else:
            exercise_text = "Exercise: None"
            confidence_text = "Confidence: 0.00"
            color = (0, 0, 255)

        draw_text_enhanced(frame, exercise_text, (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, color, thickness_normal)
        y_pos += line_height
        draw_text_enhanced(frame, confidence_text, (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, color, thickness_normal)
        y_pos += line_height + 10

        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 15

        draw_text_enhanced(frame, "Counts & Calories:", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_normal, (255, 255, 255), thickness_normal)
        y_pos += line_height + 5

        counts = self.counter.get_counts()
        calories = self.counter.get_calories()

        for exercise in self.target_exercises:
            count = counts[exercise]
            calorie = calories[exercise]

            exercise_names = {
                'barbell biceps curl': 'Biceps',
                'hammer curl': 'Hammer',
                'push-up': 'Push-up',
                'shoulder press': 'Shoulder',
                'squat': 'Squat'
            }

            short_name = exercise_names.get(exercise, exercise)
            count_text = f"{short_name:8}: {count:2d}r {calorie:4.1f}c"

            text_color = (255, 255, 255)
            if count > 0:
                text_color = (0, 255, 255)

            draw_text_enhanced(frame, count_text, (panel_x + 15, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale_small, text_color, thickness_small)
            y_pos += 20

        y_pos += 8
        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 15

        total_reps = sum(counts.values())
        total_calories = self.counter.get_total_calories()

        draw_text_enhanced(frame, f"Total: {total_reps}r", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_normal, (255, 255, 0), thickness_normal)
        y_pos += line_height
        draw_text_enhanced(frame, f"Calories: {total_calories:.1f}", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_normal, (255, 255, 0), thickness_normal)
        y_pos += line_height + 15

        draw_text_enhanced(frame, f"FPS: {fps}", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, (255, 255, 0), thickness_normal)
        y_pos += line_height + 15

        controls = [
            "Q: Quit",
            "R: Reset",
            "S: Save Record",
            "D: Debug Mode"
        ]

        for control in controls:
            draw_text_enhanced(frame, control, (panel_x + 15, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), thickness_small)
            y_pos += 18

    def run_realtime_recognition(self):
        """运行实时识别 - 电脑版本"""
        if self.counter is None:
            self.initialize_system()

        # 使用OpenCV打开摄像头
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("无法打开摄像头")
            return

        # 设置摄像头参数
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

        window_name = '健身动作识别系统 (电脑版)'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)

        print("电脑端实时识别系统启动中...")
        if self.simulation_mode:
            print("注意：当前运行在模拟模式")
        else:
            print(f"ONNX推理提供者: {self.onnx_session.get_providers()}")
        print("按 'q' 退出，'r' 重置计数，'s' 保存记录，'d' 切换调试模式")

        fps_counter = 0
        fps_timer = time.time()
        current_fps = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)

                predicted_exercise, confidence, landmarks = self.predict_exercise(frame)

                frame = self.draw_pose_landmarks(frame, landmarks)

                if predicted_exercise and predicted_exercise in self.target_exercises:
                    self.counter.update_counts(predicted_exercise, confidence, landmarks)

                self._draw_info_panel(frame, predicted_exercise, confidence, current_fps)

                fps_counter += 1
                if time.time() - fps_timer > 1.0:
                    current_fps = fps_counter
                    fps_counter = 0
                    fps_timer = time.time()

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.counter.reset_counts()
                    print("计数和卡路里已重置")
                elif key == ord('s'):
                    self._save_workout_record()
                elif key == ord('d'):
                    self.debug_mode = not self.debug_mode
                    print(f"调试模式: {'开启' if self.debug_mode else '关闭'}")

        except KeyboardInterrupt:
            print("\n收到中断信号，正在退出...")
        except Exception as e:
            print(f"运行时错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("摄像头已关闭")

    def _save_workout_record(self):
        """保存训练记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workout_record_{timestamp}.json"

        counts = self.counter.get_counts()
        calories = self.counter.get_calories()
        total_calories = self.counter.get_total_calories()

        record = {
            "timestamp": datetime.now().isoformat(),
            "device": "PC",
            "user_profile": {
                "body_weight": self.user_profile.body_weight,
                "age": self.user_profile.age,
                "gender": self.user_profile.gender,
                "added_weights": self.user_profile.added_weights
            },
            "exercises": counts,
            "calories": calories,
            "total_reps": sum(counts.values()),
            "total_calories": total_calories,
            "exercise_details": {},
            "mode": "simulation" if self.simulation_mode else "onnx_pc",
            "inference_provider": self.onnx_session.get_providers() if self.onnx_session else None
        }

        for exercise in self.target_exercises:
            debug_info = self.counter.get_exercise_info(exercise)
            record["exercise_details"][exercise] = {
                "count": counts[exercise],
                "calories": calories[exercise],
                "calories_per_rep": debug_info['calories_per_rep'] if debug_info else 0,
                "avg_duration": debug_info['avg_rep_duration'] if debug_info else 0,
                "angle_range": f"{debug_info['min_angle_seen']:.1f}-{debug_info['max_angle_seen']:.1f}"
                if debug_info and debug_info['min_angle_seen'] != float('inf') else "N/A"
            }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=4, ensure_ascii=False)

            print(f"训练记录已保存: {filename}")
            print(f"本次训练总计: {sum(counts.values())} 次动作, {total_calories:.1f} 卡路里")
        except Exception as e:
            print(f"保存记录失败: {e}")


def test_counter_only_pc():
    """仅测试计数功能的简化版本 - 电脑版"""
    print("计数功能测试模式 (电脑版)")
    print("=" * 40)

    user_profile = UserProfile()
    user_profile.load_from_input()
    calorie_calculator = CalorieCalculator()

    target_exercises = ['barbell biceps curl', 'hammer curl', 'push-up', 'shoulder press', 'squat']
    counter = ExerciseCounterOptimized(target_exercises, user_profile, calorie_calculator)

    feature_extractor = RealtimeFeatureExtractor()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    window_name = 'Exercise Counter Test (PC)'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    print("测试模式启动...")
    print("手动选择要测试的动作：")
    print("按 '1': push-up")
    print("按 '2': shoulder press")
    print("按 '3': barbell biceps curl")
    print("按 '4': squat")
    print("按 '5': hammer curl")
    print("按 'R': 重置计数")
    print("按 'Q': 退出")

    current_exercise = None
    fps_counter = 0
    fps_timer = time.time()
    current_fps = 0

    def draw_pose_simple(frame, landmarks):
        if landmarks is None or len(landmarks) < 132:
            return frame

        landmarks_reshaped = landmarks[:132].reshape(-1, 4)
        height, width = frame.shape[:2]

        key_points = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in key_points:
            if idx < len(landmarks_reshaped):
                point = landmarks_reshaped[idx]
                if point[3] > 0.5:
                    x = int(point[0] * width)
                    y = int(point[1] * height)
                    if 0 <= x < width and 0 <= y < height:
                        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                        cv2.circle(frame, (x, y), 5, (255, 255, 255), 2)

        connections = [(11, 13), (13, 15), (12, 14), (14, 16), (11, 12), (23, 24)]
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks_reshaped) and end_idx < len(landmarks_reshaped):
                start_point = landmarks_reshaped[start_idx]
                end_point = landmarks_reshaped[end_idx]
                if start_point[3] > 0.5 and end_point[3] > 0.5:
                    start_x = int(start_point[0] * width)
                    start_y = int(start_point[1] * height)
                    end_x = int(end_point[0] * width)
                    end_y = int(end_point[1] * height)
                    if (0 <= start_x < width and 0 <= start_y < height and
                            0 <= end_x < width and 0 <= end_y < height):
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 3)
        return frame

    def draw_compact_test_ui(frame, current_exercise, counts, calories, fps):
        height, width = frame.shape[:2]

        panel_width = 300
        panel_x = width - panel_width - 10

        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, 10), (width - 10, 400), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        cv2.rectangle(frame, (panel_x, 10), (width - 10, 400), (255, 255, 255), 3)

        font_scale_title = 0.7
        font_scale_normal = 0.6
        font_scale_small = 0.5
        thickness_title = 2
        thickness_normal = 2
        line_height = 25
        y_pos = 40

        draw_text_enhanced(frame, "Exercise Counter Test", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_title, (0, 255, 255), thickness_title)
        y_pos += 30

        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 20

        if current_exercise:
            draw_text_enhanced(frame, f"Testing: {current_exercise[:12]}...", (panel_x + 15, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, (0, 255, 0), thickness_normal)
        else:
            draw_text_enhanced(frame, "Select exercise (1-5)", (panel_x + 15, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, (255, 255, 0), thickness_normal)
        y_pos += line_height + 10

        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 15

        draw_text_enhanced(frame, "Counts & Calories:", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_DUPLEX, font_scale_normal, (255, 255, 255), thickness_normal)
        y_pos += line_height + 5

        exercise_names = {
            'barbell biceps curl': 'Biceps',
            'hammer curl': 'Hammer',
            'push-up': 'Push-up',
            'shoulder press': 'Shoulder',
            'squat': 'Squat'
        }

        for exercise in target_exercises:
            count = counts[exercise]
            calorie = calories[exercise]
            color = (0, 255, 0) if exercise == current_exercise else (255, 255, 255)
            short_name = exercise_names.get(exercise, exercise)

            draw_text_enhanced(frame, f"{short_name:8}: {count:2d}r {calorie:4.1f}c",
                               (panel_x + 15, y_pos), cv2.FONT_HERSHEY_SIMPLEX, font_scale_small, color, 1)
            y_pos += 20

        y_pos += 8
        cv2.line(frame, (panel_x + 15, y_pos), (width - 25, y_pos), (255, 255, 255), 2)
        y_pos += 18

        total_calories = sum(calories.values())
        draw_text_enhanced(frame, f"Total: {sum(counts.values())}r {total_calories:.1f}c",
                           (panel_x + 15, y_pos), cv2.FONT_HERSHEY_DUPLEX, font_scale_normal, (255, 255, 0),
                           thickness_normal)
        y_pos += line_height + 15

        draw_text_enhanced(frame, f"FPS: {fps}", (panel_x + 15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale_normal, (255, 255, 0), thickness_normal)
        y_pos += line_height + 15

        controls = ["1-5: Select", "R: Reset", "Q: Quit"]
        for control in controls:
            draw_text_enhanced(frame, control, (panel_x + 15, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y_pos += 18

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            landmarks = feature_extractor.extract_landmarks_from_frame(frame)

            frame = draw_pose_simple(frame, landmarks)

            if current_exercise and landmarks is not None:
                counter.update_counts(current_exercise, 0.8, landmarks)

            counts = counter.get_counts()
            calories = counter.get_calories()
            draw_compact_test_ui(frame, current_exercise, counts, calories, current_fps)

            fps_counter += 1
            if time.time() - fps_timer > 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_timer = time.time()

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('r') or key == ord('R'):
                counter.reset_counts()
                print("计数和卡路里已重置")
            elif key == ord('1'):
                current_exercise = 'push-up'
                print(f"开始测试: {current_exercise}")
            elif key == ord('2'):
                current_exercise = 'shoulder press'
                print(f"开始测试: {current_exercise}")
            elif key == ord('3'):
                current_exercise = 'barbell biceps curl'
                print(f"开始测试: {current_exercise}")
            elif key == ord('4'):
                current_exercise = 'squat'
                print(f"开始测试: {current_exercise}")
            elif key == ord('5'):
                current_exercise = 'hammer curl'
                print(f"开始测试: {current_exercise}")

    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
    finally:
        print("正在清理资源...")
        cap.release()
        cv2.destroyAllWindows()

        print("\n测试完成！最终结果:")
        for exercise in target_exercises:
            count = counts[exercise]
            calorie = calories[exercise]
            print(f"  {exercise}: {count} 次, {calorie:.2f} 卡路里")
        total_calories = sum(calories.values())
        print(f"  总计: {sum(counts.values())} 次, {total_calories:.2f} 卡路里")


def main():
    """主函数 - 电脑版"""
    print("健身动作识别与卡路里计算系统 (电脑版)")
    print("=" * 60)

    try:
        system = ExerciseRecognitionSystemPC()

        print("\n启动实时摄像头模式...")
        print("提示：按 'd' 键可以切换到调试模式查看详细信息")
        system.run_realtime_recognition()

    except Exception as e:
        print(f"系统运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("请选择运行模式:")
    print("1. 完整系统（含卡路里计算）- 电脑版")
    print("2. 仅测试计数功能 - 电脑版")

    mode = input("请选择 (1 或 2): ").strip()

    if mode == '1':
        main()
    elif mode == '2':
        test_counter_only_pc()
    else:
        print("无效选择，启动完整系统...")
        main()
