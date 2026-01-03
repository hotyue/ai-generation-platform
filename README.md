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
```

---

## 🚀 快速启动（Docker）

> 前置条件：
> - Docker >= 24
> - Docker Compose Plugin

```bash
git clone <your-repo-url>
cd ai-generation-platform
docker compose up -d --build
```

---

启动后默认服务：

服务	地址

前端	http://localhost:8080

后端 API	http://localhost:8000

PostgreSQL	localhost:5432

---

⚙️ 配置说明

后端环境变量（示例）

DATABASE_URL=postgresql://aiweb_user:password@db:5432/aiweb

JWT_SECRET=your-secret-key

COMFYUI_BASE_URL=http://your-comfyui-node:9000


前端环境变量

VITE_API_BASE=/api

---

📘 文档导航

详细设计与部署说明统一放在 docs/：

- 系统架构总览：docs/00_overview.md

- Docker 生产部署白皮书：docs/01_deployment_docker.md

- 系统架构设计：docs/02_architecture.md

- 数据库设计：docs/03_database.md

- 安全与鉴权模型：docs/04_security.md

- 版本冻结与演进策略：docs/05_versioning.md

---

🧭 项目演进概览（v1.0.0-beta → v1.0.31）

AI Generation Platform 自 v1.0.0-beta 起进入真实运行阶段，随后各版本围绕“可用 → 可控 → 可交付”的目标逐步演进：

v1.0.0-beta
项目首次上线运行，系统进入真实用户与真实数据驱动的生产阶段。

v1.0.1
对上线后的核心行为进行梳理与收敛，使系统从“能用”迈向“可解释、可定位”。

v1.0.2
强化任务状态与异常路径的可追踪性，为稳定运行与后续演进奠定基础。

v1.0.3
对部署与工程实践进行修正，消除早期 Docker 化过程中暴露的问题。

v1.0.4
进行安全与配置治理专项修复，完善私密配置与运行环境隔离。

v1.0.5
完成后端容器化与交付形态固化，形成稳定可复现的后端运行基线。

v1.0.6
完成前端工程治理与 Docker 化，前后端交付形态全面对齐，形成可长期支持的工程基线。

v1.0.7 ～ v1.0.9
在真实运行基础上持续校准核心业务链路，逐步厘清生成任务、用户状态与配额之间的事实边界。

v1.0.10 ～ v1.0.14
引入事实推进与裁决机制，使系统状态从流程驱动转向事实驱动，奠定长期治理基础。

v1.0.15 ～ v1.0.20
建立账号状态、荣誉系统与配额的一致性模型，前后端在裁决与展示职责上完成解耦。

v1.0.21 ～ v1.0.29
通过多轮事实回写与窗口冻结，核心系统语义被正式固化，项目治理体系在工程实践中稳定运行。

v1.0.30
对生成成功判定、历史记录与事实推进纪律进行系统性收敛，形成稳定、不可歧义的功能基线版本。

v1.0.31
在不改变成功裁决模型的前提下引入归档吸收机制，使生成结果具备长期可交付与可回溯能力。


---

📄 License

This project is licensed under the MIT License.