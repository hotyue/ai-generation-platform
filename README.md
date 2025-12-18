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

产品演进路径（v0 → v1.0.4）
阶段一：原型与早期开发（v1.0 之前）

项目最初以验证 AI 生成链路的可行性为目标，完成了以下基础能力：

后端 API 服务

前端交互界面

AI 生成引擎的集成与调度

基础用户认证与任务流程

该阶段以快速验证为主，配置管理与工程治理遵循早期开发阶段的常见实践。

阶段二：v1.0.0-beta（首次进入实际运行状态）

自 v1.0.0-beta 起，项目正式进入 真实运行阶段，具备以下特征：

系统完成部署并对外提供服务

存在真实用户与真实生成请求

数据持久化存储于关系型数据库

用户认证、配额与任务状态逻辑开始被实际依赖

从该版本开始，项目不再被视为可随意重建的原型系统，
后续版本的演进均需保证数据与行为的连续性。

阶段三：v1.0.1 ～ v1.0.3（稳定性与工程治理阶段）

v1.0.1 至 v1.0.3 版本主要用于：

稳定核心业务流程

明确系统状态与行为边界

提升异常处理与可追溯性

对齐前后端与任务执行逻辑

该阶段未引入显著的新业务功能，重点在于将系统从“可运行”推进至“可维护、可解释”。

阶段四：v1.0.4（安全修复与工程基线固化）

v1.0.4 为一次 安全修复与工程基线治理版本（Security Hotfix）。

在对项目早期工程历史进行复核时，确认曾存在以下情况：

部分私密配置（如数据库连接信息、数据库用户密码、JWT 签名密钥）

在早期开发阶段被误提交至版本控制系统

v1.0.4 中完成的治理工作

对包含私密配置的历史提交执行重写与清理

对数据库用户密码及 JWT 签名密钥完成轮换

私密配置统一通过运行环境变量注入，不再存在于源码或可提交文件中

后端配置加载方式统一，支持 systemd 与 Docker 运行场景

提供 .env.example 作为交付级配置模板，避免真实配置进入版本控制

v1.0.4 的范围说明

不引入任何新功能

不修改任何 API 行为

不涉及业务逻辑调整

该版本仅用于安全治理与配置管理规范化。

安全与配置基线（v1.0.4 起）

自 v1.0.4 起，项目遵循以下配置与安全原则：

源码与版本库中不包含任何真实私密信息

所有敏感配置均通过运行环境变量注入

提供模板文件用于部署指导，不包含真实值

版本历史在可审计前提下避免暴露敏感数据

版本策略说明

v1.0.x 系列以稳定性、安全治理与工程基线固化为主

安全修复版本可能不包含任何功能变更

新功能与商业化能力将在后续版本中引入

当前状态

当前版本：v1.0.4

版本类型：安全修复版本（Security Hotfix）

向后兼容性：保持兼容

工程状态：生产可用基线

后续演进

在 v1.0.4 所建立的安全与工程基线之上，
项目将继续推进后续功能与能力扩展，同时保持对安全性与可维护性的约束。

---

📄 License

This project is licensed under the MIT License.