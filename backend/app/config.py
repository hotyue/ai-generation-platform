import os

COMFY_API_BASE = os.getenv("COMFY_API_BASE")

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not COMFY_API_BASE:
    raise RuntimeError("COMFY_API_BASE is not set")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")
