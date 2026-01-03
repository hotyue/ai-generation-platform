BEGIN;

-- v1.0.32
-- histories 表新增执行与用户耗时相关事实字段
-- 所有时间字段统一采用 UTC（TIMESTAMP WITH TIME ZONE）

ALTER TABLE histories
    ADD COLUMN started_at TIMESTAMP WITH TIME ZONE NULL,
    ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE NULL,
    ADD COLUMN total_elapsed_time INTEGER NULL;

COMMENT ON COLUMN histories.started_at IS
    '任务实际开始执行时间（UTC），仅用于内部执行统计';

COMMENT ON COLUMN histories.completed_at IS
    '任务最终完成时间（UTC），定义为 archive_url 写入完成时间';

COMMENT ON COLUMN histories.total_elapsed_time IS
    '任务真实完成耗时（秒），定义为 completed_at - created_at，仅用于历史页面展示';

COMMIT;
