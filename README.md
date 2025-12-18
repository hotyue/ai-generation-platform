```markdown
# AI Generation Platform

AI 图像生成平台（FastAPI + Vue + Docker）

*An AI image generation platform built with FastAPI, Vue, and Docker.*

---

## 📌 项目简介 | Project Overview

**AI Generation Platform** 是一个面向真实用户与真实业务场景的 AI 图像生成平台。

项目采用 **前后端分离 + 三容器 Docker 架构**，并与 **ComfyUI 算力节点解耦运行**，从一开始即按照生产系统标准设计。

主要特性包括：

- 用户体系与鉴权
- 配额 / 套餐 / 计费逻辑
- 生成任务与历史记录
- 管理后台
- 可长期演进的容器化部署结构

---

## 🧱 系统架构 | System Architecture

```text
Frontend (Vue + Nginx)
        |
        |  /api/*
        v
Backend (FastAPI)
        |
        v
PostgreSQL

ComfyUI
- 独立算力节点
- HTTP API 调用
📂 目录结构 | Repository Structure
text
复制代码
ai-generation-platform/
├── backend/                 # FastAPI 后端
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── init_aiweb.sql
│
├── frontend/
│   └── ai-web-g1/            # Vue 前端
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── .env.production
│       └── src/
│
├── docker-compose.yml        # 前端 / 后端 / 数据库
├── docker/                   # 预留 Docker 扩展
├── scripts/                  # 运维脚本
├── README.md
└── .gitignore
🐳 Docker 架构 | Docker Architecture
本项目采用 三容器生产级架构：

容器	说明
frontend	Vue 构建产物 + Nginx
backend	FastAPI + Gunicorn
db	PostgreSQL 14

设计原则：

镜像无状态（Stateless）

数据通过 Volume 持久化

所有配置通过环境变量注入

ComfyUI 不纳入 docker-compose

🚀 快速启动 | Quick Start
1️⃣ 环境要求
Linux（推荐 Ubuntu 22.04）

Docker 24+

Docker Compose Plugin

bash
复制代码
docker -v
docker compose version
2️⃣ 启动服务
在项目根目录执行：

bash
复制代码
docker compose up -d --build
服务地址：

服务	地址
前端	http://localhost:8080
后端	http://localhost:8000
数据库	localhost:5432

3️⃣ 停止服务
bash
复制代码
docker compose down
🔧 环境变量 | Environment Variables
后端（docker-compose.yml）
env
复制代码
DATABASE_URL=postgresql://aiweb_user:***@db:5432/aiweb
JWT_SECRET=***
COMFYUI_BASE_URL=http://<comfyui-host>:9000
前端（.env.production）
env
复制代码
VITE_API_BASE=/api
前端环境变量仅在构建阶段生效。

🔐 安全约定 | Security Notes
不要提交真实密码或生产密钥

数据库 Volume 不应随意删除

所有生成行为必须可审计

不允许在生产环境随意重建数据库

🧭 版本治理 | Version Governance
v1.0.0-beta：生产基线版本（已冻结）

后续版本仅允许增量演进

不允许回滚或篡改历史行为语义

📚 文档规划 | Documentation Plan
建议后续新增：

text
复制代码
docs/
├── architecture.md
├── deployment.md
├── api.md
├── database.md
└── version-ledger.md
🧠 设计理念 | Design Philosophy
这是一个真实运行的工程系统，而不是 Demo。

事实优先于设计

数据优先于重构

稳定优先于炫技

📄 License
Private / Internal Use