# backend/app/config_history_advancer.py
import os


def _get_int(name: str, default: int) -> int:
    """
    从环境变量读取整数配置。
    若值存在但不是合法整数，则直接抛出异常，避免隐性错误。
    """
    value = os.getenv(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        raise RuntimeError(f"{name} must be an integer, got: {value}")


# =========================
# Facts Advancer 基础扫描配置
# =========================

# 每轮扫描间隔（秒）
SCAN_INTERVAL_SECONDS = _get_int(
    "HISTORY_SCAN_INTERVAL_SECONDS",
    3,
)

# pending 状态最大等待时间（秒）
# 超过该时间仍未生成成功，则判定为 failed
TIMEOUT_SECONDS = _get_int(
    "HISTORY_TIMEOUT_SECONDS",
    60,
)

# 单轮最多处理的 history 数量
BATCH_SIZE = _get_int(
    "HISTORY_BATCH_SIZE",
    20,
)


# =========================
# 归档吸收窗口配置（v1.0.31）
# =========================

# 生成成功后，允许吸收 archive_url 的时间窗口（秒）
ARCHIVE_ABSORB_WINDOW_SECONDS = _get_int(
    "HISTORY_ARCHIVE_ABSORB_WINDOW_SECONDS",
    60,
)
