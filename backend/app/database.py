import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import DATABASE_URL

logger = logging.getLogger("database")

# ==========================================
# ⭐ 核心修缮：数据库引擎智能挂载引擎 (支持 MariaDB & PostgreSQL)
# ==========================================
# 针对 MySQL/MariaDB 家族，增加 pool_recycle 防止连接在空闲时被数据库强行掐断 (MySQL 默认为 8 小时)
engine_kwargs = {"pool_pre_ping": True}

if DATABASE_URL.startswith("mysql"):
    engine_kwargs["pool_recycle"] = 3600
    logger.info("[Database] MariaDB/MySQL engine initialized with pool_recycle=3600")
elif DATABASE_URL.startswith("postgresql"):
    logger.info("[Database] PostgreSQL engine initialized")

try:
    engine = create_engine(DATABASE_URL, **engine_kwargs)
except Exception as e:
    logger.error(f"[Database] Failed to create engine. Check DATABASE_URL: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()