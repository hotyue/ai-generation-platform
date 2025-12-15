# AI Generation Platform

AI Generation Platform is a full-stack web platform for AI image generation, built with **FastAPI**, **Vue**, and **ComfyUI**.  
It provides a complete solution including user authentication, quota management, task orchestration, and real-time status updates.

---

## ✨ Features

- User authentication & authorization
- AI image generation based on ComfyUI workflows
- Task queue and generation history
- Quota & plan management
- Real-time task status (WebSocket / SSE ready)
- Admin panel for user & plan management
- Frontend–backend separation
- Docker-ready architecture

---

## 🏗️ Project Structure

```text
ai-generation-platform/
├── backend/        # FastAPI backend
│   └── app/
│       ├── main.py
│       ├── routers/
│       ├── models/
│       ├── schemas/
│       ├── utils/
│       └── ws/
├── frontend/       # Vue frontend
│   └── ai-web-g1/
├── docker/         # Docker-related files (build & runtime)
└── README.md


🚀 Tech Stack
Backend

FastAPI

SQLAlchemy

JWT Authentication

WebSocket / SSE

Frontend

Vue 3

Vite

Pinia

Axios

AI / Infra

ComfyUI

Docker

Redis (optional, planned)

🧪 Development Status

Current stage: v1.0.0-beta

Actively under development

APIs and internal structure may change before stable release

📦 Versioning

This project follows Semantic Versioning:
vMAJOR.MINOR.PATCH[-stage]

Examples:

v1.0.0-beta.0

v1.0.0

v1.0.1

📄 License

License will be added when the project is ready for public release.

---

# 四、推荐的 Release 命名规范（你马上就能用）

当你推送 `v1.0.0-beta.0` tag 后：

- **Release title**  
  ```text
  AI Generation Platform v1.0.0-beta.0

Release description（示例）
- Initial baseline import
- Backend: FastAPI core structure
- Frontend: Vue-based user interface
- User system, quota management, and generation history
