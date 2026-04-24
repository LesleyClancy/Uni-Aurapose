CREATE DATABASE IF NOT EXISTS profitai
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE profitai;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  openid VARCHAR(96) NOT NULL UNIQUE,
  nickname VARCHAR(80) NOT NULL DEFAULT 'AuraPose User',
  avatar_url VARCHAR(500) NULL,
  gender ENUM('male', 'female', 'unknown') NOT NULL DEFAULT 'unknown',
  age TINYINT UNSIGNED NULL,
  height_cm DECIMAL(5,2) NULL,
  weight_kg DECIMAL(5,2) NULL,
  level_no INT UNSIGNED NOT NULL DEFAULT 1,
  streak_days INT UNSIGNED NOT NULL DEFAULT 0,
  title VARCHAR(120) NOT NULL DEFAULT 'Fitness Explorer',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS body_metrics (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  weight_kg DECIMAL(5,2) NULL,
  body_fat_pct DECIMAL(5,2) NULL,
  calories_burned INT UNSIGNED NOT NULL DEFAULT 0,
  recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_body_metrics_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_body_metrics_user_time (user_id, recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS courses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  title VARCHAR(120) NOT NULL,
  category VARCHAR(64) NOT NULL,
  difficulty VARCHAR(40) NOT NULL,
  duration_minutes INT UNSIGNED NOT NULL,
  calories INT UNSIGNED NOT NULL DEFAULT 0,
  description VARCHAR(500) NOT NULL,
  image_url VARCHAR(500) NOT NULL DEFAULT '/static/logo.png',
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS training_modules (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  exercise_key VARCHAR(80) NOT NULL,
  title VARCHAR(120) NOT NULL,
  category VARCHAR(64) NOT NULL,
  target_muscle VARCHAR(120) NOT NULL,
  difficulty VARCHAR(40) NOT NULL,
  recommended_weight_kg DECIMAL(5,2) NULL,
  target_reps INT UNSIGNED NULL,
  ai_tip VARCHAR(500) NOT NULL,
  image_url VARCHAR(500) NOT NULL DEFAULT '/static/logo.png',
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_training_modules_exercise (exercise_key),
  INDEX idx_training_modules_active (is_active, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS challenges (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  title VARCHAR(120) NOT NULL,
  badge VARCHAR(60) NOT NULL,
  category VARCHAR(64) NOT NULL,
  duration_days INT UNSIGNED NOT NULL,
  minutes_per_day INT UNSIGNED NOT NULL,
  description VARCHAR(500) NOT NULL,
  image_url VARCHAR(500) NOT NULL DEFAULT '/static/logo.png',
  sort_order INT NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS training_sessions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  module_id BIGINT UNSIGNED NULL,
  exercise_key VARCHAR(80) NULL,
  status ENUM('active', 'finished', 'cancelled') NOT NULL DEFAULT 'active',
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at DATETIME NULL,
  duration_seconds INT UNSIGNED NOT NULL DEFAULT 0,
  total_reps INT UNSIGNED NOT NULL DEFAULT 0,
  total_calories DECIMAL(8,2) NOT NULL DEFAULT 0,
  best_accuracy DECIMAL(5,2) NOT NULL DEFAULT 0,
  avg_accuracy DECIMAL(5,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_training_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_training_sessions_module FOREIGN KEY (module_id) REFERENCES training_modules(id) ON DELETE SET NULL,
  INDEX idx_training_sessions_user_time (user_id, started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS training_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  session_id BIGINT UNSIGNED NOT NULL,
  exercise_key VARCHAR(80) NOT NULL,
  reps INT UNSIGNED NOT NULL DEFAULT 0,
  calories DECIMAL(8,2) NOT NULL DEFAULT 0,
  accuracy DECIMAL(5,2) NOT NULL DEFAULT 0,
  fps INT UNSIGNED NOT NULL DEFAULT 0,
  raw_counts JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_training_records_session FOREIGN KEY (session_id) REFERENCES training_sessions(id) ON DELETE CASCADE,
  INDEX idx_training_records_session_time (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS achievements (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  title VARCHAR(120) NOT NULL,
  description VARCHAR(500) NOT NULL,
  icon VARCHAR(80) NOT NULL,
  rule_key VARCHAR(80) NOT NULL,
  threshold_value INT UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_achievements (
  user_id BIGINT UNSIGNED NOT NULL,
  achievement_id BIGINT UNSIGNED NOT NULL,
  progress_value INT UNSIGNED NOT NULL DEFAULT 0,
  unlocked_at DATETIME NULL,
  PRIMARY KEY (user_id, achievement_id),
  CONSTRAINT fk_user_achievements_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_user_achievements_achievement FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
