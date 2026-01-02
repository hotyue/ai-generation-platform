import os
import boto3
from typing import Optional, Dict

# =====================================================
# Cloudflare R2 基础配置（来自运行环境）
# =====================================================

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_PUBLIC_BASE = os.getenv("R2_PUBLIC_BASE")

R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# =====================================================
# S3 Client（惰性初始化，进程级单例）
# =====================================================

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            region_name="auto",
        )
    return _s3_client


# =====================================================
# 底层上传函数（冻结行为，不改语义）
# =====================================================

def upload_to_r2(local_path: str, object_key: str) -> Optional[str]:
    """
    Cloudflare R2 上传（冻结行为）：

    - 成功：返回 archive 公网 URL
    - 失败：返回 None
    - 不抛异常
    """
    try:
        s3 = get_s3_client()
        s3.upload_file(
            local_path,
            R2_BUCKET,
            object_key,
            ExtraArgs={"ContentType": "image/png"},
        )
        return f"{R2_PUBLIC_BASE}/{object_key}"
    except Exception:
        return None


# =====================================================
# v1.0.31 裁决级封装（新增，允许使用）
# =====================================================

def archive_image(local_path: str, object_key: str) -> Dict[str, Optional[str]]:
    """
    archive 裁决级封装（v1.0.31）

    返回结构（冻结）：
    {
        "archive_status": "success" | "failed",
        "archive_url": str | None,
        "archive_error": str | None
    }

    设计原则：
    - 不抛异常
    - 不做重试
    - 不做时间判断
    - 只基于 R2 返回事实裁决
    """
    try:
        archive_url = upload_to_r2(local_path, object_key)

        if archive_url:
            return {
                "archive_status": "success",
                "archive_url": archive_url,
                "archive_error": None,
            }

        return {
            "archive_status": "failed",
            "archive_url": None,
            "archive_error": "upload_failed",
        }

    except Exception as e:
        # 理论兜底，不应成为主路径
        return {
            "archive_status": "failed",
            "archive_url": None,
            "archive_error": str(e),
        }
