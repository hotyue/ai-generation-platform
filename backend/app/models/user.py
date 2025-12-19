from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey
from datetime import datetime
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 账号基础信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    # 联系方式
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)

    # 商业属性
    role = Column(String(20), default="user")  # user / admin
    quota = Column(BigInteger, default=0)      # 剩余可用生成次数或积分

    # 账户状态
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    # 展示信息
    avatar_url = Column(String(255), nullable=True)
    remark = Column(String(255), nullable=True)  # 备注，预留给运营使用

    # 邀请关系（可用于推广）
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    invitation_code = Column(String(50), unique=True, nullable=True)

    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
