from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    task_id = Column(String(100), index=True, nullable=False)
    prompt = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    
    # 新增：任务状态
    status = Column(String(20), default="pending")  # pending / success / failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
