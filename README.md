AI Generation Platform

AI 图像生成平台（FastAPI + Vue + Docker）

📌 项目简介 | Project Overview

AI Generation Platform 是一个面向真实用户与真实业务场景的 AI 图像生成平台，
采用 前后端分离 + 三容器 Docker 架构，并与 ComfyUI 算力节点解耦运行。

项目从一开始即按 生产系统标准设计，具备完整的：

用户体系

配额 / 套餐 / 计费逻辑

生成任务与历史记录

后台管理能力

可演进的容器化部署结构

🧱 系统架构 | System Architecture
┌──────────────┐
│   Frontend   │  Vue 3 + Vite + Nginx
│  (Container) │  :80
└──────┬───────┘
       │  /api/*
┌──────▼───────┐
│   Backend    │  FastAPI + Gunicorn
│  (Container) │  :8000
└──────┬───────┘
       │
┌──────▼───────┐
│   Database   │  PostgreSQL 14
│  (Container) │  :5432
└──────────────┘

ComfyUI（算力节点）
- 独立服务器 / 容器
- 通过 HTTP API 调用

📂 目录结构 | Repository Structure
ai-generation-platform/
├── backend/                 # 后端 FastAPI 服务
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── init_aiweb.sql
│
├── frontend/
│   └── ai-web-g1/            # 前端 Vue 项目
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── .env.production
│       └── src/
│
├── docker-compose.yml        # 三容器编排（前端 / 后端 / 数据库）
├── docker/                   # 预留：未来 Docker 扩展
├── scripts/                  # 运维 / 初始化脚本
├── README.md                 # 项目总说明（本文件）
└── .gitignore

🐳 Docker 架构说明 | Docker Design

本项目采用 三容器生产架构：

容器	说明
frontend	Vue 构建产物 + Nginx，负责页面与反向代理
backend	FastAPI + Gunicorn，负责业务逻辑
db	PostgreSQL 14，持久化用户与业务数据
关键原则

镜像无状态（Stateless）

数据通过 Volume 持久化

配置通过环境变量注入

ComfyUI 不纳入本 Compose

🚀 快速启动（Docker） | Quick Start (Docker)
1️⃣ 准备环境

Linux（推荐 Ubuntu 22.04）

Docker ≥ 24

Docker Compose Plugin

docker -v
docker compose version

2️⃣ 启动服务

在项目根目录执行：

docker compose up -d --build


启动后：

服务	地址
前端	http://localhost:8080

后端 API	http://localhost:8000

数据库	localhost:5432
3️⃣ 停止服务
docker compose down

🔧 环境变量说明 | Environment Variables
后端（docker-compose.yml）
DATABASE_URL=postgresql://aiweb_user:***@db:5432/aiweb
JWT_SECRET=***
COMFYUI_BASE_URL=http://<comfyui-host>:9000

前端（frontend/ai-web-g1/.env.production）
VITE_API_BASE=/api


⚠️ 前端只认 构建期环境变量，运行时不读取 .env

🔐 安全与约定 | Security & Conventions

.env.production、真实密码 禁止提交到公开仓库

数据库 Volume 不可随意删除

所有生成行为 必须可审计

不允许在生产环境“随意重建数据库”

🧭 版本治理 | Version Governance

v1.0.0-beta：已冻结（生产基线）

后续版本仅允许 增量演进

不允许回滚、篡改历史行为语义

📚 文档规划建议 | Documentation Strategy

建议后续新增专用文档目录：

docs/
├── architecture.md      # 架构设计说明
├── deployment.md        # 部署与运维
├── api.md               # API 规范
├── database.md          # 数据库结构说明
└── version-ledger.md    # 版本事实记录

🧠 设计理念 | Design Philosophy

这是一个真实运行的工程系统，不是 Demo。

事实优先于设计

数据优先于重构

可解释性优先于“炫技”

稳定优先于速度

📄 License

Private / Internal Use
（如需开源或商业授权，请另行声明）