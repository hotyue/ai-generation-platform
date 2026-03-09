-- ========================================================
-- AI Platform - MariaDB 11 Initialization (Baseline v1.0.36)
-- Converted from PostgreSQL schema v1.0.32
-- ========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. Table: users
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL,
  `password_hash` VARCHAR(128) NOT NULL,
  `email` VARCHAR(100),
  `phone` VARCHAR(20),
  `role` VARCHAR(20) DEFAULT 'user',
  `quota` BIGINT DEFAULT 0,
  `is_active` TINYINT(1) DEFAULT 1,
  `is_deleted` TINYINT(1) DEFAULT 0,
  `avatar_url` VARCHAR(255),
  `remark` VARCHAR(255),
  `inviter_id` INT,
  `invitation_code` VARCHAR(50),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login_at` DATETIME,
  `account_status` VARCHAR(16) NOT NULL DEFAULT 'normal',
  `total_success_tasks` INT NOT NULL DEFAULT 0,
  `level_star` INT NOT NULL DEFAULT 0,
  `level_moon` INT NOT NULL DEFAULT 0,
  `level_sun` INT NOT NULL DEFAULT 0,
  `level_diamond` INT NOT NULL DEFAULT 0,
  `level_crown` INT NOT NULL DEFAULT 0,
  `user_fact_consumed_at` DATETIME,
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_phone` (`phone`),
  UNIQUE KEY `users_invitation_code_key` (`invitation_code`),
  INDEX `idx_users_account_status` (`account_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 2. Table: histories
-- ----------------------------
CREATE TABLE IF NOT EXISTS `histories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT,
  `task_id` VARCHAR(100) NOT NULL,
  `prompt` TEXT NOT NULL,
  `image_url` VARCHAR(500),
  `archive_url` VARCHAR(500),
  `status` VARCHAR(20) DEFAULT 'pending',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `honor_consumed_at` DATETIME,
  `user_fact_consumed_at` DATETIME,
  `started_at` DATETIME COMMENT '任务实际开始执行时间（UTC），仅用于内部执行统计',
  `completed_at` DATETIME COMMENT '任务最终完成时间（UTC），定义为 archive_url 写入完成时间',
  `total_elapsed_time` INT COMMENT '任务真实完成耗时（秒），定义为 completed_at - created_at',
  INDEX `ix_histories_task_id` (`task_id`),
  INDEX `idx_histories_honor_consumed_at` (`honor_consumed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 3. Table: honor_level_events
-- ----------------------------
CREATE TABLE IF NOT EXISTS `honor_level_events` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `trigger` VARCHAR(50) NOT NULL,
  `before_total_success_tasks` INT NOT NULL,
  `after_total_success_tasks` INT NOT NULL,
  `before_star` INT NOT NULL,
  `after_star` INT NOT NULL,
  `before_moon` INT NOT NULL,
  `after_moon` INT NOT NULL,
  `before_sun` INT NOT NULL,
  `after_sun` INT NOT NULL,
  `before_diamond` INT NOT NULL,
  `after_diamond` INT NOT NULL,
  `before_crown` INT NOT NULL,
  `after_crown` INT NOT NULL,
  `reward_quota_delta` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 4. Table: plans
-- ----------------------------
CREATE TABLE IF NOT EXISTS `plans` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `description` VARCHAR(255),
  `quota` INT NOT NULL,
  `duration_days` INT,
  `price` DECIMAL(10,2) DEFAULT 0.00,
  `is_active` TINYINT(1) DEFAULT 1,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 5. Table: quota_logs
-- ----------------------------
CREATE TABLE IF NOT EXISTS `quota_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `change_val` INT NOT NULL COMMENT 'Mapping from pg change column',
  `reason` VARCHAR(255) NOT NULL,
  `operator_id` INT,
  `related_plan_id` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_quota_logs_user_id` (`user_id`),
  INDEX `idx_quota_logs_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 注意：quota_logs 的 change 字段在 MySQL 中是保留字，后端通常通过 SQLAlchemy 依然能兼容，
-- 这里为了避免底层建表报错，我们将其暂时设为 change_val 或使用反引号包裹。
-- 这里的建表我们已经安全处理。

ALTER TABLE `quota_logs` CHANGE `change_val` `change` INT NOT NULL;

SET FOREIGN_KEY_CHECKS = 1;
