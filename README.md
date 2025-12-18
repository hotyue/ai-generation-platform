AI Generation Platform

AI Generation Platform 是一个已上线运行的 AI 图像生成平台，采用前后端分离架构，基于 FastAPI + Vue + PostgreSQL，并以 Docker 作为标准交付与运行形态。

📌 项目状态说明（非常重要）

当前版本：v1.0.0-beta（已冻结）

系统已进入真实运行状态

已存在真实用户、真实生成任务、真实数据库数据

本仓库不是 Demo / Sample / Toy Project

📄 版本冻结与演进规则请见：
👉 docs/VERSIONING.md

🧱 系统总体架构
┌─────────────┐
│   Frontend  │  Vue + Nginx (Docker)
│   (HTTP)    │
└──────┬──────┘
       │ /api
       ▼
┌─────────────┐
│   Backend   │  FastAPI + Gunicorn (Docker)
│             │
└──────┬──────┘
       │ SQL
       ▼
┌─────────────┐
│ PostgreSQL  │  数据持久化 (Docker Volume)
└─────────────┘

外部算力：
ComfyUI（独立服务器，通过 HTTP 调用）


前端为 唯一公网入口

后端仅通过内部网络暴露

数据库不对公网开放

ComfyUI 不纳入本仓库 Docker 编排

📁 仓库目录结构
.
├── backend/                 # 后端（FastAPI）
│   ├── app/                 # 业务代码
│   ├── Dockerfile           # 后端生产镜像
│   ├── requirements.txt
│   ├── init_aiweb.sql
│
├── frontend/
│   └── ai-web-g1/            # 前端（Vue）
│       ├── Dockerfile        # 前端生产镜像（Vue Build + Nginx）
│       ├── nginx.conf        # 前端反向代理配置
│       ├── .env.production   # 前端生产环境变量
│       └── src/
│
├── docker-compose.yml        # 三容器编排（frontend + backend + db）
├── docs/                     # 项目级文档（建议）
│   └── VERSIONING.md
├── scripts/                  # 运维 / 初始化脚本（预留）
└── README.md

🐳 Docker 化运行（推荐方式）
1️⃣ 前置条件

Docker ≥ 24

Docker Compose Plugin（docker compose）

已安装并运行 Docker 服务

验证：

docker -v
docker compose version

2️⃣ 启动完整系统

在项目根目录执行：

docker compose up -d --build


启动后容器包括：

aiweb-frontend

aiweb-backend

aiweb-db

3️⃣ 访问入口
服务	地址
前端	http://localhost:8080

后端 API（内部）	http://backend:8000

数据库	内部容器网络
⚙️ 核心环境变量说明
Backend（docker-compose.yml）
DATABASE_URL=postgresql://aiweb_user:***@db:5432/aiweb
JWT_SECRET=***
COMFYUI_BASE_URL=http://<comfyui-host>:9000

Frontend（.env.production）
VITE_API_BASE=/api


前端通过 Nginx 将 /api 反向代理到后端容器

🔐 权限与角色

用户体系基于 JWT

内置角色：

普通用户

管理员（admin）

所有权限裁决 仅在后端完成

📜 版本与演进规则

当前冻结版本：v1.0.0-beta

后续版本 不得破坏：

用户模型

配额逻辑

生成 / 历史行为

Docker 三容器架构

📄 详见：docs/VERSIONING.md

🚫 特别声明（禁止事项）

❌ 不假设数据库可重建

❌ 不删除已有数据语义

❌ 不绕过后端直接访问数据库 / 算力

❌ 不以“重构”为理由破坏稳定逻辑

📦 后续规划（非本版本内容）

CDN / 对象存储

异步任务队列

多算力节点调度

CI/CD 自动镜像发布

上述内容 不属于 v1.0.0-beta 冻结范围

📄 License

Private Project
All Rights Reserved.