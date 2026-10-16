from flask import Flask, request, jsonify, send_from_directory
import base64
import json
import cv2
import numpy as np
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError
from uuid import uuid4

from old import ExerciseRecognitionSystemPC
from db import DatabaseUnavailable, execute, fetch_all, fetch_one, healthcheck


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "saved_models"
DEFAULT_POSE_TASK = BASE_DIR / "pose_landmarker_full.task"
MAX_INPUT_WIDTH = int(os.getenv("MAX_INPUT_WIDTH", "160"))
DEFAULT_OPENID = "dev-openid"
AVATAR_UPLOAD_DIR = BASE_DIR / "uploads" / "avatars"
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

EXERCISE_LABELS = {
    "barbell biceps curl": "杠铃弯举",
    "hammer curl": "锤式弯举",
    "push-up": "俯卧撑",
    "shoulder press": "肩推",
    "squat": "深蹲",
    "unknown": "未识别",
}

EXERCISE_MET = {
    "push-up": 8.0,
    "squat": 5.0,
    "hammer curl": 5.5,
    "barbell biceps curl": 6.0,
    "shoulder press": 6.5,
}


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


def ensure_report_table():
    execute(
        """
        CREATE TABLE IF NOT EXISTS training_reports (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          user_id BIGINT UNSIGNED NOT NULL,
          session_id BIGINT UNSIGNED NOT NULL,
          title VARCHAR(160) NOT NULL,
          summary JSON NOT NULL,
          insights JSON NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT fk_training_reports_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
          CONSTRAINT fk_training_reports_session FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE CASCADE,
          UNIQUE KEY uq_training_reports_session (session_id),
          INDEX idx_training_reports_user_time (user_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def json_loads_safe(value, fallback=None):
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


def coerce_int(value):
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def coerce_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def truthy(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def app_env(name, fallback=""):
    return os.getenv(name, fallback).strip()


def wechat_appid():
    return app_env("WECHAT_APPID") or app_env("WX_APPID") or app_env("MP_WEIXIN_APPID")


def wechat_app_secret():
    return app_env("WECHAT_APP_SECRET") or app_env("WX_APP_SECRET") or app_env("MP_WEIXIN_APP_SECRET")


def allow_dev_wechat_fallback():
    return truthy(os.getenv("WECHAT_LOGIN_DEV_FALLBACK", "true"))


def build_dev_openid(code=None):
    suffix = code or f"{int(time.time())}"
    return f"wx-dev-{suffix}"


def resolve_wechat_openid(code=None, explicit_openid=None):
    if explicit_openid:
        return explicit_openid

    appid = wechat_appid()
    secret = wechat_app_secret()
    if not code:
        if allow_dev_wechat_fallback():
            return build_dev_openid()
        raise ValueError("missing wechat login code")

    if not appid or not secret:
        if allow_dev_wechat_fallback():
            return build_dev_openid(code)
        raise RuntimeError("missing WECHAT_APPID or WECHAT_APP_SECRET")

    query = urllib_parse.urlencode(
        {
            "appid": appid,
            "secret": secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    url = f"https://api.weixin.qq.com/sns/jscode2session?{query}"

    try:
        with urllib_request.urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        if allow_dev_wechat_fallback():
            return build_dev_openid(code)
        raise RuntimeError(f"wechat code2session failed: {exc}") from exc

    if payload.get("errcode"):
        if allow_dev_wechat_fallback():
            return build_dev_openid(code)
        raise RuntimeError(payload.get("errmsg") or "wechat code2session error")

    openid = payload.get("openid")
    if not openid:
        if allow_dev_wechat_fallback():
            return build_dev_openid(code)
        raise RuntimeError("wechat login response missing openid")
    return openid


def ensure_column(table_name, column_name, definition_sql):
    row = fetch_one(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table_name, column_name),
    )
    if row:
        return
    execute(f"ALTER TABLE {table_name} ADD COLUMN {definition_sql}")


_schema_ready = False


def ensure_app_schema():
    global _schema_ready

    if _schema_ready:
        return

    ensure_column(
        "users",
        "profile_completed_at",
        "profile_completed_at DATETIME NULL DEFAULT NULL AFTER weight_kg",
    )
    ensure_column(
        "training_sessions",
        "session_rpe",
        "session_rpe TINYINT UNSIGNED NULL DEFAULT NULL AFTER avg_accuracy",
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS recovery_checkins (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
          user_id BIGINT UNSIGNED NOT NULL,
          recorded_on DATE NOT NULL,
          prs_score TINYINT UNSIGNED NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          CONSTRAINT fk_recovery_checkins_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
          UNIQUE KEY uq_recovery_checkins_user_day (user_id, recorded_on),
          INDEX idx_recovery_checkins_user_time (user_id, recorded_on)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
    _schema_ready = True


def clamp_score(value, minimum=0, maximum=10):
    parsed = coerce_int(value)
    if parsed is None:
        return None
    return max(minimum, min(maximum, parsed))


def safe_gender(value):
    return value if value in {"male", "female", "unknown"} else "unknown"


def extract_user_payload(payload=None):
    payload = payload or {}
    return {
        "openid": payload.get("openid"),
        "nickname": payload.get("nickname") or payload.get("nickName") or "AuraPose User",
        "avatar_url": payload.get("avatar_url") or payload.get("avatarUrl"),
        "gender": safe_gender(payload.get("gender") or "unknown"),
        "age": coerce_int(payload.get("age")),
        "height_cm": coerce_float(payload.get("height_cm") or payload.get("height")),
        "weight_kg": coerce_float(payload.get("weight_kg") or payload.get("weight")),
        "body_fat_pct": coerce_float(payload.get("body_fat_pct")),
        "profile_completed": truthy(payload.get("profile_completed") or payload.get("profileCompleted")),
    }


def is_user_profile_complete(user_row):
    if not user_row:
        return False
    return bool(user_row.get("profile_completed_at"))


def normalize_user_row(row):
    normalized = normalize_row(row)
    if not normalized:
        return None
    normalized["profile_completed"] = is_user_profile_complete(normalized)
    return normalized


def absolute_media_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{request.url_root.rstrip('/')}{path}"


def get_or_create_user(openid=None, payload=None):
    ensure_app_schema()
    profile = extract_user_payload(payload)
    openid = openid or profile["openid"] or DEFAULT_OPENID
    profile_completed_at = datetime.utcnow() if profile["profile_completed"] else None

    execute(
        """
        INSERT INTO users (openid, nickname, avatar_url, gender, age, height_cm, weight_kg, profile_completed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nickname = COALESCE(NULLIF(VALUES(nickname), ''), nickname),
            avatar_url = COALESCE(NULLIF(VALUES(avatar_url), ''), avatar_url),
            gender = CASE WHEN VALUES(gender) = 'unknown' THEN gender ELSE VALUES(gender) END,
            age = COALESCE(VALUES(age), age),
            height_cm = COALESCE(VALUES(height_cm), height_cm),
            weight_kg = COALESCE(VALUES(weight_kg), weight_kg),
            profile_completed_at = COALESCE(profile_completed_at, VALUES(profile_completed_at)),
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            openid,
            profile["nickname"],
            profile["avatar_url"],
            profile["gender"],
            profile["age"],
            profile["height_cm"],
            profile["weight_kg"],
            profile_completed_at,
        ),
    )
    return fetch_one("SELECT * FROM users WHERE openid = %s", (openid,))


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
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.form:
        return request.form.to_dict()
    return {}


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


def get_recovery_status(user_id):
    latest = fetch_one(
        """
        SELECT recorded_on, prs_score, updated_at
        FROM recovery_checkins
        WHERE user_id = %s
        ORDER BY recorded_on DESC
        LIMIT 1
        """,
        (user_id,),
    )
    today = fetch_one(
        """
        SELECT recorded_on, prs_score, updated_at
        FROM recovery_checkins
        WHERE user_id = %s AND recorded_on = CURDATE()
        LIMIT 1
        """,
        (user_id,),
    )
    return {
        "latest": normalize_row(latest) or {},
        "today": normalize_row(today) or {},
    }


def save_recovery_checkin(user_id, prs_score):
    execute(
        """
        INSERT INTO recovery_checkins (user_id, recorded_on, prs_score)
        VALUES (%s, CURDATE(), %s)
        ON DUPLICATE KEY UPDATE
            prs_score = VALUES(prs_score),
            updated_at = CURRENT_TIMESTAMP
        """,
        (user_id, prs_score),
    )
    return get_recovery_status(user_id)


def build_date_series(days):
    start = datetime.utcnow().date() - timedelta(days=days - 1)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(days)]


def get_progress_snapshot(user_id, days=7):
    days = 28 if int(days or 7) >= 28 else 7
    cutoff = datetime.utcnow() - timedelta(days=days)
    overview = fetch_one(
        """
        SELECT
            COUNT(*) AS sessions,
            COUNT(DISTINCT DATE(started_at)) AS active_days,
            COALESCE(SUM(duration_seconds), 0) AS total_seconds,
            COALESCE(SUM(total_reps), 0) AS total_reps,
            COALESCE(SUM(total_calories), 0) AS total_calories,
            COALESCE(SUM(CASE
                WHEN session_rpe IS NULL THEN 0
                ELSE session_rpe * (duration_seconds / 60.0)
            END), 0) AS total_session_load,
            COUNT(session_rpe) AS rated_sessions
        FROM training_sessions
        WHERE user_id = %s
          AND status = 'finished'
          AND started_at >= %s
        """,
        (user_id, cutoff),
    )
    daily_rows = normalize_rows(
        fetch_all(
            """
            SELECT
                DATE(started_at) AS day,
                COUNT(*) AS sessions,
                COALESCE(SUM(duration_seconds), 0) AS total_seconds,
                COALESCE(SUM(total_reps), 0) AS total_reps,
                COALESCE(SUM(total_calories), 0) AS total_calories,
                COALESCE(SUM(CASE
                    WHEN session_rpe IS NULL THEN 0
                    ELSE session_rpe * (duration_seconds / 60.0)
                END), 0) AS session_load
            FROM training_sessions
            WHERE user_id = %s
              AND status = 'finished'
              AND started_at >= %s
            GROUP BY DATE(started_at)
            ORDER BY day ASC
            """,
            (user_id, cutoff),
        )
    )
    points_by_day = {row["day"]: row for row in daily_rows}
    daily = []
    for day in build_date_series(days):
        row = points_by_day.get(day, {})
        daily.append(
            {
                "day": day,
                "sessions": int(row.get("sessions") or 0),
                "total_seconds": int(row.get("total_seconds") or 0),
                "total_reps": int(row.get("total_reps") or 0),
                "total_calories": round(float(row.get("total_calories") or 0), 1),
                "session_load": round(float(row.get("session_load") or 0), 1),
            }
        )

    session_pbs = fetch_one(
        """
        SELECT
            COALESCE(MAX(total_reps), 0) AS max_total_reps,
            COALESCE(MAX(duration_seconds), 0) AS max_duration_seconds,
            COALESCE(MAX(total_calories), 0) AS max_total_calories,
            COALESCE(MAX(CASE
                WHEN session_rpe IS NULL THEN 0
                ELSE session_rpe * (duration_seconds / 60.0)
            END), 0) AS max_session_load
        FROM training_sessions
        WHERE user_id = %s AND status = 'finished'
        """,
        (user_id,),
    )
    exercise_pbs = normalize_rows(
        fetch_all(
            """
            SELECT tr.exercise_key, MAX(tr.reps) AS best_reps
            FROM training_records tr
            JOIN training_sessions ts ON ts.id = tr.session_id
            WHERE ts.user_id = %s
              AND ts.status = 'finished'
              AND tr.exercise_key <> 'unknown'
            GROUP BY tr.exercise_key
            ORDER BY best_reps DESC, tr.exercise_key ASC
            LIMIT 5
            """,
            (user_id,),
        )
    )

    normalized_overview = normalize_row(overview) or {}
    normalized_pbs = normalize_row(session_pbs) or {}
    return {
        "range_days": days,
        "overview": {
            "sessions": int(normalized_overview.get("sessions") or 0),
            "active_days": int(normalized_overview.get("active_days") or 0),
            "total_seconds": int(normalized_overview.get("total_seconds") or 0),
            "total_reps": int(normalized_overview.get("total_reps") or 0),
            "total_calories": round(float(normalized_overview.get("total_calories") or 0), 1),
            "total_session_load": round(float(normalized_overview.get("total_session_load") or 0), 1),
            "rated_sessions": int(normalized_overview.get("rated_sessions") or 0),
        },
        "daily": daily,
        "pbs": {
            "max_total_reps": int(normalized_pbs.get("max_total_reps") or 0),
            "max_duration_seconds": int(normalized_pbs.get("max_duration_seconds") or 0),
            "max_total_calories": round(float(normalized_pbs.get("max_total_calories") or 0), 1),
            "max_session_load": round(float(normalized_pbs.get("max_session_load") or 0), 1),
        },
        "exercise_pbs": [
            {
                "exercise_key": row.get("exercise_key") or "unknown",
                "best_reps": int(row.get("best_reps") or 0),
            }
            for row in exercise_pbs
        ],
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
    total_reps = int(response.get("total_reps") or reps or 0)
    total_calories = float(response.get("total_calories") or calories or 0)
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
        (exercise_key, total_reps, total_calories, accuracy, session_id, session_id),
    )


def latest_counts_from_records(records):
    latest_counts = {}
    for record in records:
        raw_counts = json_loads_safe(record.get("raw_counts"), {})
        if isinstance(raw_counts, dict):
            for key, value in raw_counts.items():
                latest_counts[key] = max(int(value or 0), latest_counts.get(key, 0))

    if latest_counts:
        return latest_counts

    fallback = {}
    for record in records:
        key = record.get("exercise_key") or "unknown"
        fallback[key] = max(int(record.get("reps") or 0), fallback.get(key, 0))
    return fallback


def build_training_report(session, records):
    counts = latest_counts_from_records(records)
    total_reps = int(session.get("total_reps") or sum(counts.values()) or 0)
    total_calories = float(session.get("total_calories") or 0)
    duration_seconds = int(session.get("duration_seconds") or 0)
    avg_accuracy = float(session.get("avg_accuracy") or 0)
    best_accuracy = float(session.get("best_accuracy") or 0)

    exercise_items = []
    total_counted = sum(counts.values())
    for key, reps in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        if reps <= 0:
            continue
        met = EXERCISE_MET.get(key, 5.0)
        calories = total_calories * reps / total_counted if total_counted else 0
        exercise_items.append(
            {
                "key": key,
                "label": EXERCISE_LABELS.get(key, key),
                "reps": int(reps),
                "calories": round(calories, 1),
                "percent": round((reps / total_counted) * 100, 1) if total_counted else 0,
                "intensity": "高强度" if met >= 6 else "中强度" if met >= 4 else "低强度",
            }
        )

    dominant = exercise_items[0] if exercise_items else {"label": "未识别", "key": "unknown", "reps": 0}
    intensity_score = round(total_reps + total_calories / 10 + avg_accuracy / 2, 1)
    completion_level = "优秀" if avg_accuracy >= 85 and total_reps >= 30 else "稳定" if total_reps >= 12 else "起步"

    timeline = []
    first_created = None
    for record in records:
        created_at = record.get("created_at")
        if first_created is None:
            first_created = created_at
        elapsed = 0
        if created_at and first_created:
            try:
                elapsed = int((created_at - first_created).total_seconds())
            except TypeError:
                elapsed = len(timeline)
        timeline.append(
            {
                "time": elapsed,
                "reps": int(record.get("reps") or 0),
                "accuracy": round(float(record.get("accuracy") or 0), 1),
            }
        )

    suggestions = []
    if avg_accuracy < 70:
        suggestions.append("动作稳定性偏低，下一次建议放慢节奏，优先保证轨迹完整。")
    else:
        suggestions.append("动作识别稳定，可以在保持姿态的基础上逐步增加组数。")
    if dominant.get("key") in {"push-up", "shoulder press", "barbell biceps curl", "hammer curl"}:
        suggestions.append("本次以上肢训练为主，下一次可加入深蹲来平衡下肢刺激。")
    elif dominant.get("key") == "squat":
        suggestions.append("本次下肢占比较高，训练后注意髋膝踝拉伸与恢复。")
    if duration_seconds < 180:
        suggestions.append("训练时长较短，可尝试 3-5 分钟热身后再进入正式检测。")
    else:
        suggestions.append("训练时长达标，建议保留 1-2 分钟整理放松。")

    summary = {
        "session_id": session["id"],
        "started_at": normalize_value(session.get("started_at")),
        "ended_at": normalize_value(session.get("ended_at")),
        "duration_seconds": duration_seconds,
        "total_reps": total_reps,
        "total_calories": round(total_calories, 1),
        "avg_accuracy": round(avg_accuracy, 1),
        "best_accuracy": round(best_accuracy, 1),
        "dominant_exercise": dominant,
        "completion_level": completion_level,
        "intensity_score": intensity_score,
        "exercise_items": exercise_items,
        "timeline": timeline[-24:],
    }
    insights = {
        "headline": f"{dominant.get('label', '训练')}完成度{completion_level}",
        "suggestions": suggestions,
        "focus": dominant.get("label", "未识别"),
    }
    return summary, insights


def upsert_training_report(session_id):
    ensure_report_table()
    session = fetch_one(
        """
        SELECT s.*, u.id AS user_id, u.nickname
        FROM training_sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = %s
        """,
        (session_id,),
    )
    if not session:
        return None

    records = fetch_all(
        """
        SELECT exercise_key, reps, calories, accuracy, raw_counts, created_at
        FROM training_records
        WHERE session_id = %s
        ORDER BY created_at ASC, id ASC
        """,
        (session_id,),
    )
    summary, insights = build_training_report(session, records)
    title = f"{insights['focus']}训练报告"
    summary_json = json.dumps(summary, ensure_ascii=False)
    insights_json = json.dumps(insights, ensure_ascii=False)

    execute(
        """
        INSERT INTO training_reports (user_id, session_id, title, summary, insights)
        VALUES (%s, %s, %s, CAST(%s AS JSON), CAST(%s AS JSON))
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            summary = VALUES(summary),
            insights = VALUES(insights)
        """,
        (session["user_id"], session_id, title, summary_json, insights_json),
    )
    report = fetch_one("SELECT * FROM training_reports WHERE session_id = %s", (session_id,))
    return normalize_report_row(report)


def normalize_report_row(row):
    normalized = normalize_row(row)
    if not normalized:
        return None
    normalized["summary"] = json_loads_safe(normalized.get("summary"), {})
    normalized["insights"] = json_loads_safe(normalized.get("insights"), {})
    return normalized


def decode_image_bytes(image_bytes):
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


def decode_base64_image(image_data):
    if not image_data:
        raise ValueError("No image data provided")

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    image_bytes = base64.b64decode(image_data)
    return decode_image_bytes(image_bytes)


def decode_uploaded_image(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No uploaded image provided")

    image_bytes = uploaded_file.read()
    if not image_bytes:
        raise ValueError("Uploaded image is empty")
    return decode_image_bytes(image_bytes)


def decode_request_image(data):
    uploaded_file = request.files.get("image")
    if uploaded_file is not None:
        return decode_uploaded_image(uploaded_file)
    return decode_base64_image(data.get("image"))


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
    try:
        ensure_app_schema()
    except Exception:
        pass
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


@app.route("/media/avatars/<path:filename>", methods=["GET"])
def serve_avatar(filename):
    return send_from_directory(AVATAR_UPLOAD_DIR, filename)


@app.route("/api/uploads/avatar", methods=["POST"])
def upload_avatar():
    try:
        uploaded_file = request.files.get("file")
        if uploaded_file is None or not uploaded_file.filename:
            return jsonify({"error": "avatar_required", "message": "missing avatar file"}), 400

        suffix = Path(uploaded_file.filename).suffix.lower() or ".png"
        if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
            suffix = ".png"

        filename = f"{uuid4().hex}{suffix}"
        save_path = AVATAR_UPLOAD_DIR / filename
        uploaded_file.save(save_path)
        media_path = f"/media/avatars/{filename}"
        return jsonify({"url": absolute_media_url(media_path), "path": media_path})
    except Exception as exc:
        return jsonify({"error": "avatar_upload_failed", "message": str(exc)}), 500


@app.route("/api/auth/wechat-login", methods=["POST"])
def wechat_login():
    try:
        data = request_payload()
        openid = resolve_wechat_openid(code=data.get("code"), explicit_openid=data.get("openid"))
        user = get_or_create_user(openid=openid, payload=data)
        return jsonify(
            {
                "token": openid,
                "openid": openid,
                "user": normalize_user_row(user),
                "needs_profile": not is_user_profile_complete(user),
            }
        )
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/upsert", methods=["POST"])
def upsert_user():
    try:
        data = request_payload()
        user = get_or_create_user(payload=data)
        profile = extract_user_payload(data)
        if profile.get("weight_kg") is not None or profile.get("body_fat_pct") is not None:
            execute(
                """
                INSERT INTO body_metrics (user_id, weight_kg, body_fat_pct, calories_burned)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user["id"],
                    profile.get("weight_kg"),
                    profile.get("body_fat_pct"),
                    int(data.get("calories_burned") or 0),
                ),
            )
        fresh_user = fetch_one("SELECT * FROM users WHERE id = %s", (user["id"],))
        return jsonify({"user": normalize_user_row(fresh_user)})
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
                "user": normalize_user_row(user),
                "summary": summary,
                "achievements": achievements,
            }
        )
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/<openid>/recovery", methods=["GET"])
def user_recovery(openid):
    try:
        user = get_or_create_user(openid=openid)
        return jsonify(get_recovery_status(user["id"]))
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/<openid>/recovery", methods=["POST"])
def save_user_recovery(openid):
    try:
        user = get_or_create_user(openid=openid)
        data = request_payload()
        prs_score = clamp_score(data.get("prs_score"))
        if prs_score is None:
            return jsonify({"error": "invalid_prs_score", "message": "prs_score must be between 0 and 10"}), 400
        return jsonify(save_recovery_checkin(user["id"], prs_score))
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/users/<openid>/progress", methods=["GET"])
def user_progress(openid):
    try:
        user = get_or_create_user(openid=openid)
        days = int(request.args.get("days", 7))
        return jsonify(get_progress_snapshot(user["id"], days=days))
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/app/bootstrap", methods=["GET"])
def app_bootstrap():
    try:
        user = current_user_from_request()
        return jsonify(
            {
                "user": normalize_user_row(user),
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
        session_rpe = clamp_score(data.get("session_rpe"), minimum=1, maximum=10)
        system.counter.reset_counts()
        session_id = execute(
            """
            INSERT INTO training_sessions (user_id, module_id, exercise_key, session_rpe)
            VALUES (%s, %s, %s, %s)
            """,
            (user["id"], module_id, exercise_key, session_rpe),
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
        session_rpe = clamp_score(data.get("session_rpe"), minimum=1, maximum=10)
        execute(
            """
            UPDATE training_sessions
            SET status = 'finished',
                ended_at = COALESCE(ended_at, NOW()),
                duration_seconds = GREATEST(duration_seconds, %s),
                session_rpe = COALESCE(%s, session_rpe)
            WHERE id = %s
            """,
            (duration_seconds, session_rpe, session_id),
        )
        session = fetch_one("SELECT * FROM training_sessions WHERE id = %s", (session_id,))
        report = upsert_training_report(session_id)
        return jsonify({"session": normalize_row(session), "report": report})
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


@app.route("/api/users/<openid>/reports", methods=["GET"])
def user_reports(openid):
    try:
        ensure_report_table()
        user = get_or_create_user(openid=openid)
        limit = int(request.args.get("limit", 20))
        missing = fetch_all(
            """
            SELECT s.id
            FROM training_sessions s
            LEFT JOIN training_reports r ON r.session_id = s.id
            WHERE s.user_id = %s AND s.status = 'finished' AND r.id IS NULL
            ORDER BY s.started_at DESC
            LIMIT %s
            """,
            (user["id"], limit),
        )
        for session in missing:
            upsert_training_report(session["id"])

        rows = fetch_all(
            """
            SELECT r.id, r.user_id, r.session_id, r.title, r.summary, r.insights, r.created_at,
                   s.duration_seconds, s.total_reps, s.total_calories, s.avg_accuracy
            FROM training_reports r
            JOIN training_sessions s ON s.id = r.session_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s
            """,
            (user["id"], limit),
        )
        return jsonify({"items": [normalize_report_row(row) for row in rows]})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/training/reports/<int:report_id>", methods=["GET"])
def training_report(report_id):
    try:
        ensure_report_table()
        row = fetch_one(
            """
            SELECT r.*, s.started_at, s.ended_at, s.status
            FROM training_reports r
            JOIN training_sessions s ON s.id = r.session_id
            WHERE r.id = %s
            """,
            (report_id,),
        )
        if not row:
            return jsonify({"error": "report_not_found"}), 404
        return jsonify({"report": normalize_report_row(row)})
    except Exception as exc:
        return json_db_error(exc)


@app.route("/api/detect", methods=["POST"])
def detect_exercise():
    try:
        data = request_payload()
        frame = decode_request_image(data)

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
        data = request_payload()
        decode_start = time.time()
        frame = decode_request_image(data)
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
