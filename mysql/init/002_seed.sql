USE profitai;

INSERT INTO users (openid, nickname, gender, age, height_cm, weight_kg, level_no, streak_days, title)
VALUES ('dev-openid', 'AuraPose User', 'male', 28, 180, 75, 1, 7, 'Fitness Explorer')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

INSERT INTO body_metrics (user_id, weight_kg, body_fat_pct, calories_burned, recorded_at)
SELECT id, 75.0, 17.4, 460, DATE_SUB(NOW(), INTERVAL 6 DAY) FROM users WHERE openid = 'dev-openid'
ON DUPLICATE KEY UPDATE calories_burned = VALUES(calories_burned);
INSERT INTO body_metrics (user_id, weight_kg, body_fat_pct, calories_burned, recorded_at)
SELECT id, 74.8, 17.0, 520, DATE_SUB(NOW(), INTERVAL 5 DAY) FROM users WHERE openid = 'dev-openid';
INSERT INTO body_metrics (user_id, weight_kg, body_fat_pct, calories_burned, recorded_at)
SELECT id, 74.5, 16.2, 842, NOW() FROM users WHERE openid = 'dev-openid';

INSERT INTO courses (code, title, category, difficulty, duration_minutes, calories, description, image_url, sort_order) VALUES
('core-burst', 'High Intensity Core Burst', 'strength', 'medium', 35, 380, 'Core stability and abdominal strength plan.', '/static/logo.png', 10),
('evening-stretch', 'Evening Deep Stretch', 'mobility', 'low', 20, 120, 'Recovery and mobility session for late day relaxation.', '/static/logo.png', 20),
('hiit-burn', 'HIIT Quick Burn', 'cardio', 'high', 15, 450, 'Short interval training for metabolic conditioning.', '/static/logo.png', 30)
ON DUPLICATE KEY UPDATE title = VALUES(title), description = VALUES(description), sort_order = VALUES(sort_order);

INSERT INTO training_modules
(exercise_key, title, category, target_muscle, difficulty, recommended_weight_kg, target_reps, ai_tip, image_url, sort_order) VALUES
('barbell biceps curl', 'Biceps Curl', 'strength', 'Biceps', 'medium', 12.5, 36, 'Keep elbows stable and avoid swinging your torso.', '/static/logo.png', 10),
('push-up', 'Push-up', 'strength', 'Core and chest', 'medium', NULL, 50, 'Brace your core and keep shoulder blades controlled.', '/static/logo.png', 20),
('pull-up', 'Pull-up', 'strength', 'Back', 'high', NULL, 20, 'Start with assisted reps if form drops below target.', '/static/logo.png', 30),
('squat', 'Squat', 'strength', 'Legs', 'medium', 45.0, 40, 'Rest up to 90 seconds between sets for stronger depth control.', '/static/logo.png', 40)
ON DUPLICATE KEY UPDATE title = VALUES(title), ai_tip = VALUES(ai_tip), sort_order = VALUES(sort_order);

INSERT INTO challenges (code, title, badge, category, duration_days, minutes_per_day, description, image_url, sort_order) VALUES
('strength-builder-14', '14-Day Strength Builder', 'Strength', 'strength', 14, 45, 'Progressive strength challenge with AI form tracking.', '/static/logo.png', 10),
('morning-mobility-flow', 'Morning Mobility Flow', 'Mobility', 'mobility', 7, 20, 'Low intensity mobility work for recovery.', '/static/logo.png', 20)
ON DUPLICATE KEY UPDATE title = VALUES(title), description = VALUES(description);

INSERT INTO achievements (code, title, description, icon, rule_key, threshold_value) VALUES
('streak-7', '7-Day Streak', 'Complete training on seven consecutive days.', 'local_fire_department', 'streak_days', 7),
('reps-100', '100 Reps', 'Reach 100 total recognized repetitions.', 'trophy', 'total_reps', 100),
('early-session', 'Early Session', 'Complete a morning training session.', 'star', 'morning_sessions', 1),
('deep-worker', 'Deep Work Master', 'Finish ten tracked sessions.', 'workspace_premium', 'finished_sessions', 10)
ON DUPLICATE KEY UPDATE title = VALUES(title), description = VALUES(description);
