-- unfinished tasks count
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ctm_unfinished
ON compute_task_mappings (finished_at)
WHERE finished_at IS NULL;

-- recent finished tasks for avg duration
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ctm_finished_at_desc
ON compute_task_mappings (finished_at DESC)
WHERE finished_at IS NOT NULL;
