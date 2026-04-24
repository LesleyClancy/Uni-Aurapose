from flask import Flask, request, jsonify
import base64
import json
import cv2
import numpy as np
import os
from pathlib import Path
import time
from datetime import datetime

from old import ExerciseRecognitionSystemPC
from db import DatabaseUnavailable, execute, fetch_all, fetch_one, healthcheck


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "saved_models"
DEFAULT_POSE_TASK = BASE_DIR / "pose_landmarker_full.task"
MAX_INPUT_WIDTH = 256

pose_task_env = os.getenv("MEDIAPIPE_POSE_TASK_PATH")
if pose_task_env:
    pose_task_path = Path(pose_task_env)
    if not pose_task_path.is_absolute():
        pose_task_path = BASE_DIR / pose_task_path
    if pose_task_path.exists():
        os.environ["MEDIAPIPE_POSE_TASK_PATH"] = str(pose_task_path)
elif DEFAULT_POSE_TASK.exists():
    os.environ["MEDIAPIPE_POSE_TASK_PATH"] = str(DEFAULT_POSE_TASK)

app = Flask(__name__)

system = ExerciseRecognitionSystemPC(model_dir=str(MODEL_DIR))
system.user_profile.profile_loaded = True
system.initialize_system()

_last_frame_time = None
_last_record_time_by_session = {}
_last_realtime_log_time = 0
RECORD_INTERVAL_SECONDS = 1.0
REALTIME_LOG_INTERVAL_SECONDS = 2.0


def normalize_value(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8")
    if type(value).__name__ == "Decimal":
        return float(value)
    return value


def normalize_row(row):
    if row is None:
        return None
    return {key: normalize_value(value) for key, value in row.items()}


def normalize_rows(rows):
    return [normalize_row(row) for row in rows]


def json_db_error(exc):
    status = 503 if isinstance(exc, DatabaseUnavailable) else 500
    return jsonify(
        {
            "error": "database_unavailable" if status == 503 else "database_error",
            "message": str(exc),
        }
    ), status


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/<path:_path>", methods=["OPTIONS"])
def api_options(_path):
    return "", 204


def request_payload():
    return request.get_json(silent=True) or {}


def safe_gender(value):
    return value if value in {"male", "female", "unknown"} else "unknown"


def get_or_create_user(openid=None, payload=None):
    payload = payload or {}
    openid = openid or payload.get("openid") or "dev-openid"
    nickname = payload.get("nickname") or "AuraPose User"
    gender = safe_gender(payload.get("gender") or "unknown")
    age = payload.get("age")
    height = payload.get("height") or payload.get("height_cm")
    weight = payload.get("weight") or payload.get("weight_kg")
    avatar_url = payload.get("avatar_url")

    execute(
        """
        INSERT INTO users (openid, nickname, avatar_url, gender, age, height_cm, weight_kg)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nickname = COALESCE(NULLIF(VALUES(nickname), ''), nickname),
            avatar_url = COALESCE(VALUES(avatar_url), avatar_url),
            gender = VALUES(gender),
            age = COALESCE(VALUES(age), age),
            height_cm = COALESCE(VALUES(height_cm), height_cm),
            weight_kg = COALESCE(VALUES(weight_kg), weight_kg),
            updated_at = CURRENT_TIMESTAMP
        """,
        (openid, nickname, avatar_url, gender, age, height, weight),
    )
    return fetch_one("SELECT * FROM users WHERE openid = %s", (openid,))


def current_user_from_request():
    openid = request.args.get("openid") or request_payload().get("openid") or "dev-openid"
    return get_or_create_user(openid=openid)


def get_user_summary(user_id):
    latest_metric = fetch_one(
        """
        SELECT weight_kg, body_fat_pct, calories_burned, recorded_at
        FROM body_metrics
        WHERE user_id = %s
        ORDER BY recorded_at DESC
        LIMIT 1
        """,
        (user_id,),
    )
    totals = fetch_one(
        """
        SELECT
            COALESCE(SUM(total_reps), 0) AS total_reps,
            COALESCE(SUM(total_calories), 0) AS total_calories,
            COALESCE(SUM(duration_seconds), 0) AS total_seconds,
            COALESCE(AVG(NULLIF(avg_accuracy, 0)), 0) AS avg_accuracy,
            COUNT(*) AS sessions
        FROM training_sessions
        WHERE user_id = %s AND status = 'finished'
        """,
        (user_id,),
    )
    week = fetch_all(
        """
        SELECT DATE(recorded_at) AS day, SUM(calories_burned) AS calories
        FROM body_metrics
        WHERE user_id = %s
        GROUP BY DATE(recorded_at)
        ORDER BY day DESC
        LIMIT 7
        """,
        (user_id,),
    )

    return {
        "latest_metric": normalize_row(latest_metric) or {},
        "totals": normalize_row(totals) or {},
        "weekly_calories": list(reversed(normalize_rows(week))),
    }


def list_courses(limit=20):
    return normalize_rows(
        fetch_all(
            """
            SELECT id, code, title, category, difficulty, duration_minutes, calories,
                   description, image_url
            FROM courses
            WHERE is_active = 1
            ORDER BY sort_order, id
            LIMIT %s
            """,
            (limit,),
        )
    )


def list_training_modules(limit=20):
    return normalize_rows(
        fetch_all(
            """
            SELECT id, exercise_key, title, category, target_muscle, difficulty,
                   recommended_weight_kg, target_reps, ai_tip, image_url
            FROM training_modules
            WHERE is_active = 1
            ORDER BY sort_order, id
            LIMIT %s
            """,
            (limit,),
        )
    )


def list_challenges(limit=20):
    return normalize_rows(
        fetch_all(
            """
            SELECT id, title, badge, category, duration_days, minutes_per_day,
                   description, image_url
            FROM challenges
            WHERE is_active = 1
            ORDER BY sort_order, id
            LIMIT %s
            """,
            (limit,),
        )
    )


def list_user_achievements(user_id):
    rows = fetch_all(
        """
        SELECT a.id, a.code, a.title, a.description, a.icon, a.rule_key,
               a.threshold_value, ua.progress_value, ua.unlocked_at
        FROM achievements a
        LEFT JOIN user_achievements ua
          ON ua.achievement_id = a.id AND ua.user_id = %s
        ORDER BY a.id
        """,
        (user_id,),
    )
    return normalize_rows(rows)


def log_training_record(session_id, response):
    if not session_id:
        return

    now = time.time()
    last_record_time = _last_record_time_by_session.get(str(session_id), 0)
    if now - last_record_time < RECORD_INTERVAL_SECONDS:
        return
    _last_record_time_by_session[str(session_id)] = now

    exercise_key = response.get("exercise") or "unknown"
    reps = int(response.get("reps") or 0)
    calories = float(response.get("calories") or 0)
    accuracy = float(response.get("accuracy") or 0)
    fps = int(response.get("fps") or 0)
    raw_counts = json.dumps(response.get("counts") or {}, ensure_ascii=False)

    execute(
        """
        INSERT INTO training_records
            (session_id, exercise_key, reps, calories, accuracy, fps, raw_counts)
        VALUES (%s, %s, %s, %s, %s, %s, CAST(%s AS JSON))
        """,
        (session_id, exercise_key, reps, calories, accuracy, fps, raw_counts),
    )
    execute(
        """
        UPDATE training_sessions
        SET exercise_key = COALESCE(exercise_key, %s),
            total_reps = GREATEST(total_reps, %s),
            total_calories = GREATEST(total_calories, %s),
            best_accuracy = GREATEST(best_accuracy, %s),
            avg_accuracy = (
                SELECT COALESCE(AVG(accuracy), 0)
                FROM training_records
                WHERE session_id = %s
            )
        WHERE id = %s
        """,
        (exercise_key, reps, calories, accuracy, session_id, session_id),
    )


def decode_base64_image(image_data):
    if not image_data:
        raise ValueError("No image data provided")

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("Failed to decode image")

    height, width = frame.shape[:2]
    if width > MAX_INPUT_WIDTH:
        scale = MAX_INPUT_WIDTH / float(width)
        new_size = (MAX_INPUT_WIDTH, max(1, int(height * scale)))
        frame = cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)

    return frame


def estimate_fps():
    global _last_frame_time

    now = time.time()
    if _last_frame_time is None:
        _last_frame_time = now
        return 0

    delta = now - _last_frame_time
    _last_frame_time = now
    if delta <= 0:
        return 0

    return int(round(1.0 / delta))


def build_detect_response(stats):
    predicted_exercise = stats.get("exercise")
    confidence = float(stats.get("confidence", 0.0))
    counts = stats.get("counts", {})
    calories = stats.get("calories", {})

    return {
        "exercise": predicted_exercise or "未检测到",
        "confidence": confidence,
        "reps": counts.get(predicted_exercise, 0) if predicted_exercise else 0,
        "calories": float(calories.get(predicted_exercise, 0.0)) if predicted_exercise else 0.0,
        "total_reps": int(stats.get("total_reps", 0)),
        "total_calories": float(stats.get("total_calories", 0.0)),
        "accuracy": float(confidence * 100),
        "counts": counts,
        "calories_by_exercise": calories,
    }


def serialize_landmarks(landmarks):
    if landmarks is None:
        return []

    landmarks_array = np.asarray(landmarks, dtype=np.float32)
    if landmarks_array.ndim == 1:
        if len(landmarks_array) < 132:
            padded = np.zeros(132, dtype=np.float32)
            padded[:len(landmarks_array)] = landmarks_array
            landmarks_array = padded
        landmarks_array = landmarks_array[:132].reshape(-1, 4)
    else:
        landmarks_array = landmarks_array.reshape(-1, 4)

    result = []
    for point in landmarks_array[:33]:
        result.append(
            {
                "x": float(point[0]),
                "y": float(point[1]),
                "z": float(point[2]),
                "visibility": float(point[3]),
            }
        )
    return result


@app.route("/api/health", methods=["GET"])
def health_check():
    db_ok, db_error = healthcheck()
    return jsonify(
        {
            "status": "ok",
            "model_dir": str(MODEL_DIR),
            "pose_task_path": os.getenv("MEDIAPIPE_POSE_TASK_PATH", ""),
            "simulation_mode": system.simulation_mode,
            "database": {
                "status": "ok" if db_ok else "unavailable",
                "error": db_error,
            },
        }
    )


@app.route("/api/auth/wechat-login", methods=["POST"])
def wechat_login():
    try:
        data = request_payload()
        code = data.get("code")
        openid = data.get("openid") or (f"wx-dev-{code}" if code else "dev-openid")
        user = get_or_create_user(openid=openid, payload=data)
        return jsonify({"token": openid, "openid": openid, "user": normalize_row(user)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/upsert", methods=["POST"])
def upsert_user():
    try:
        data = request_payload()
        user = get_or_create_user(payload=data)
        if data.get("weight") or data.get("weight_kg") or data.get("body_fat_pct"):
            execute(
                """
                INSERT INTO body_metrics (user_id, weight_kg, body_fat_pct, calories_burned)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user["id"],
                    data.get("weight") or data.get("weight_kg"),
                    data.get("body_fat_pct"),
                    int(data.get("calories_burned") or 0),
                ),
            )
        return jsonify({"user": normalize_row(user)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/<openid>/profile", methods=["GET"])
def user_profile(openid):
    try:
        user = get_or_create_user(openid=openid)
        summary = get_user_summary(user["id"])
        achievements = list_user_achievements(user["id"])
        return jsonify(
            {
                "user": normalize_row(user),
                "summary": summary,
                "achievements": achievements,
            }
        )
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/app/bootstrap", methods=["GET"])
def app_bootstrap():
    try:
        user = current_user_from_request()
        return jsonify(
            {
                "user": normalize_row(user),
                "summary": get_user_summary(user["id"]),
                "courses": list_courses(limit=8),
                "training_modules": list_training_modules(limit=8),
                "challenges": list_challenges(limit=8),
                "achievements": list_user_achievements(user["id"]),
            }
        )
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/courses", methods=["GET"])
def courses():
    try:
        limit = int(request.args.get("limit", 20))
        return jsonify({"items": list_courses(limit=limit)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/challenges", methods=["GET"])
def challenges():
    try:
        limit = int(request.args.get("limit", 20))
        return jsonify({"items": list_challenges(limit=limit)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/training/modules", methods=["GET"])
def training_modules():
    try:
        limit = int(request.args.get("limit", 20))
        return jsonify({"items": list_training_modules(limit=limit)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/training/sessions", methods=["POST"])
def create_training_session():
    try:
        data = request_payload()
        user = get_or_create_user(openid=data.get("openid"), payload=data)
        module_id = data.get("module_id")
        exercise_key = data.get("exercise_key")
        session_id = execute(
            """
            INSERT INTO training_sessions (user_id, module_id, exercise_key)
            VALUES (%s, %s, %s)
            """,
            (user["id"], module_id, exercise_key),
        )
        session = fetch_one("SELECT * FROM training_sessions WHERE id = %s", (session_id,))
        return jsonify({"session": normalize_row(session)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/training/sessions/<int:session_id>/finish", methods=["POST"])
def finish_training_session(session_id):
    try:
        data = request_payload()
        duration_seconds = int(data.get("duration_seconds") or 0)
        execute(
            """
            UPDATE training_sessions
            SET status = 'finished',
                ended_at = COALESCE(ended_at, NOW()),
                duration_seconds = GREATEST(duration_seconds, %s)
            WHERE id = %s
            """,
            (duration_seconds, session_id),
        )
        session = fetch_one("SELECT * FROM training_sessions WHERE id = %s", (session_id,))
        return jsonify({"session": normalize_row(session)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/<openid>/sessions", methods=["GET"])
def user_sessions(openid):
    try:
        user = get_or_create_user(openid=openid)
        limit = int(request.args.get("limit", 20))
        rows = fetch_all(
            """
            SELECT s.*, m.title AS module_title
            FROM training_sessions s
            LEFT JOIN training_modules m ON m.id = s.module_id
            WHERE s.user_id = %s
            ORDER BY s.started_at DESC
            LIMIT %s
            """,
            (user["id"], limit),
        )
        return jsonify({"items": normalize_rows(rows)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/detect", methods=["POST"])
def detect_exercise():
    try:
        data = request.get_json(silent=True) or {}
        frame = decode_base64_image(data.get("image"))

        predicted_exercise, confidence, landmarks = system.predict_exercise(frame)
        if predicted_exercise and landmarks is not None:
            system.counter.update_counts(predicted_exercise, confidence, landmarks)

        stats = system.get_runtime_stats(predicted_exercise, confidence)
        response = build_detect_response(stats)
        response["landmarks"] = serialize_landmarks(landmarks)
        if data.get("session_id"):
            try:
                log_training_record(data.get("session_id"), response)
            except Exception as db_exc:
                response["recording_error"] = str(db_exc)
        return jsonify(response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/realtime_frame", methods=["POST"])
def realtime_frame():
    global _last_realtime_log_time

    try:
        request_start = time.time()
        data = request.get_json(silent=True) or {}
        decode_start = time.time()
        frame = decode_base64_image(data.get("image"))
        decode_ms = (time.time() - decode_start) * 1000
        fps = estimate_fps()

        predict_start = time.time()
        predicted_exercise, confidence, landmarks = system.predict_exercise(frame)
        predict_ms = (time.time() - predict_start) * 1000

        update_ms = 0.0
        if predicted_exercise and landmarks is not None:
            update_start = time.time()
            system.counter.update_counts(predicted_exercise, confidence, landmarks)
            update_ms = (time.time() - update_start) * 1000

        stats_start = time.time()
        stats = system.get_runtime_stats(predicted_exercise, confidence)
        stats_ms = (time.time() - stats_start) * 1000
        response = build_detect_response(stats)
        response["fps"] = fps
        response["landmarks"] = serialize_landmarks(landmarks)
        if data.get("session_id"):
            try:
                log_training_record(data.get("session_id"), response)
            except Exception as db_exc:
                response["recording_error"] = str(db_exc)
        total_ms = (time.time() - request_start) * 1000

        now = time.time()
        if now - _last_realtime_log_time >= REALTIME_LOG_INTERVAL_SECONDS:
            _last_realtime_log_time = now
            print(
                "[realtime_frame] "
                f"decode={decode_ms:.1f}ms "
                f"predict={predict_ms:.1f}ms "
                f"update={update_ms:.1f}ms "
                f"stats={stats_ms:.1f}ms "
                f"total={total_ms:.1f}ms "
                f"exercise={predicted_exercise} "
                f"landmarks={len(response['landmarks'])}"
            )
        return jsonify(response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset_stats():
    try:
        system.counter.reset_counts()
        return jsonify({"message": "Stats reset successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
