BEGIN;

-- =====================================================
-- v1.0.32
-- 新增：算力任务映射表（平台 ↔ ComfyUI）
-- 设计目标：
-- 1. 解决 task_id ↔ comfy_prompt_id 映射问题
-- 2. 承载算力节点 / API 路由 / 执行事实
-- 3. 不影响 histories 表既有裁决语义
-- =====================================================

CREATE TABLE compute_task_mappings (
    id BIGSERIAL PRIMARY KEY,

    -- ===== 平台侧事实 =====
    task_id VARCHAR NOT NULL,               -- 平台业务 task_id（UUID）
    user_id INTEGER NULL,                   -- 冗余：便于统计 / 审计

    -- ===== 算力 / 路由事实 =====
    compute_node TEXT NOT NULL,              -- 算力节点标识（如 win-comfyui-01）
    compute_api  TEXT NOT NULL,              -- 实际使用的 compute-api 地址

    -- ===== ComfyUI 事实 =====
    comfy_prompt_id VARCHAR NOT NULL,        -- ComfyUI prompt_id

    -- ===== 执行时间事实（UTC）=====
    queued_at   TIMESTAMPTZ NULL,            -- 入 ComfyUI 队列时间
    started_at  TIMESTAMPTZ NULL,            -- 开始执行时间
    finished_at TIMESTAMPTZ NULL,            -- ComfyUI 执行完成时间

    -- ===== 执行结果冗余 =====
    item_id INTEGER NULL,                    -- ComfyUI queue item_id
    status  VARCHAR(32) NULL,                -- success / error

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE compute_task_mappings IS
    '平台任务 task_id 与 ComfyUI prompt_id 的映射及算力执行事实（v1.0.32）';

COMMENT ON COLUMN compute_task_mappings.task_id IS
    '平台侧业务 task_id（UUID）';

COMMENT ON COLUMN compute_task_mappings.comfy_prompt_id IS
    'ComfyUI 返回的 prompt_id';

COMMENT ON COLUMN compute_task_mappings.compute_node IS
    '实际执行任务的算力节点标识';

COMMENT ON COLUMN compute_task_mappings.compute_api IS
    '下发任务时使用的 compute-api 地址';

COMMENT ON COLUMN compute_task_mappings.queued_at IS
    '任务进入 ComfyUI 队列的时间（UTC）';

COMMENT ON COLUMN compute_task_mappings.started_at IS
    '任务在 ComfyUI 开始执行时间（UTC）';

COMMENT ON COLUMN compute_task_mappings.finished_at IS
    '任务在 ComfyUI 执行完成时间（UTC）';

-- =========================
-- 索引（最小且必要）
-- =========================

CREATE UNIQUE INDEX ux_compute_task_task_id
    ON compute_task_mappings(task_id);

CREATE UNIQUE INDEX ux_compute_task_comfy_prompt_id
    ON compute_task_mappings(comfy_prompt_id);

CREATE INDEX ix_compute_task_compute_node
    ON compute_task_mappings(compute_node);

CREATE INDEX ix_compute_task_status
    ON compute_task_mappings(status);

COMMIT;
