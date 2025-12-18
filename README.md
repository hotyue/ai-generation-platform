# AI Generation Platform

AI Generation Platform 是一个基于 **FastAPI + Vue + Docker** 的 AI 生成服务平台，支持用户体系、配额计费、生成任务管理，并可对接外部 AI 推理服务（如 ComfyUI）。

本仓库为 **生产可部署版本**，采用 **前端 / 后端 / 数据库 三容器架构**，适用于私有化部署、商业化运营及后续规模化扩展。

---

## ✨ 核心特性

- 用户注册 / 登录 / 鉴权（JWT）
- 角色与权限体系（Admin / User）
- 配额与套餐管理（Quota / Plans）
- AI 生成任务管理（Pending / Success / Failed）
- 历史记录与审计日志
- 前后端完全 Docker 化
- Nginx 反向代理与 SPA 路由支持
- 可对接外部 ComfyUI 推理节点

---

## 🧱 技术栈

**后端**
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Gunicorn + UvicornWorker

**前端**
- Vue 3
- Vite
- Pinia
- Axios
- Nginx（生产运行）

**运维**
- Docker
- Docker Compose

---

## 📦 项目结构

> 说明：以下结构为仓库真实布局的概览（省略 node_modules/dist/venv 等运行态目录）。

```text
ai-generation-platform/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   ├── init_aiweb.sql
│   ├── requirements.txt
│   └── requirements.lock.txt
├── frontend/
│   └── ai-web-g1/
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── .env.production
│       └── src/
├── docker-compose.yml
├── docs/
├── scripts/
└── README.md
🚀 快速启动（Docker）
1) 克隆并启动
bash
复制代码
git clone <your-repo-url>
cd ai-generation-platform
docker compose up -d --build
2) 默认服务地址
服务	地址
前端（Nginx）	http://localhost:8080
后端 API（FastAPI）	http://localhost:8000
PostgreSQL	localhost:5432

⚙️ 配置说明
后端关键环境变量（docker-compose.yml 注入）
env
复制代码
DATABASE_URL=postgresql://aiweb_user:password@db:5432/aiweb
JWT_SECRET=your-secret-key
COMFYUI_BASE_URL=http://your-comfyui-node:9000
前端环境变量（生产构建）
前端文件位置：

text
复制代码
frontend/ai-web-g1/.env.production
建议值（Docker + Nginx 反代场景）：

env
复制代码
VITE_API_BASE=/api
📘 文档导航
详细设计与部署说明统一放在 docs/：

系统架构总览：docs/00_overview.md

Docker 生产部署白皮书：docs/01_deployment_docker.md

系统架构设计：docs/02_architecture.md

数据库设计：docs/03_database.md

安全与鉴权模型：docs/04_security.md

版本冻结与演进策略：docs/05_versioning.md

🧊 版本状态
当前版本：v1.0.0-beta（已冻结）

本版本作为生产基线

后续功能在 v1.1+ 演进

冻结范围与约束详见 docs/05_versioning.md

📄 License
MIT