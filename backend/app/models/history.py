from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from backend.app.database import Base


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    task_id = Column(String(100), index=True, nullable=False)

    prompt = Column(String(500), nullable=False)

    image_url = Column(String(500), nullable=True)

    # 任务状态：pending / success / failed
    status = Column(String(20), default="pending", nullable=False)

    # 生成事实创建时间（UTC，naive）
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=True,
    )

    # 荣誉系统消费标记时间（UTC，naive）
    # 仅由 Honor Facts Advancer 写入
    honor_consumed_at = Column(
        DateTime,
        nullable=True,
    )
