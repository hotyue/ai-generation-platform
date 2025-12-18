AI Generation Platform
Architecture Whitepaper（架构白皮书）
1. 文档定位与法律地位

本文档用于正式描述 AI Generation Platform 在 v1.0.0-beta 阶段已经形成并被验证的系统架构事实。

1.1 法律地位

本文档属于 架构级事实文档

优先级：

README.md
  ↓
ARCHITECTURE.md（本文档）
  ↓
DEPLOYMENT / OPERATIONS / 开发文档


本文档 不描述未来设想

本文档 不包含实验性设计

2. 系统整体架构概览
2.1 架构风格

前后端完全解耦

Docker 作为唯一标准运行与交付形态

数据与计算解耦（算力节点外置）

API 为唯一业务事实入口

2.2 架构拓扑图（逻辑）
┌────────────────────────────┐
│          Client            │
│  Browser / Mobile Web      │
└─────────────┬──────────────┘
              │ HTTP
              ▼
┌────────────────────────────┐
│        Frontend             │
│  Vue + Nginx (Docker)       │
│  - SPA                      │
│  - API Reverse Proxy        │
└─────────────┬──────────────┘
              │ /api
              ▼
┌────────────────────────────┐
│         Backend             │
│  FastAPI + Gunicorn         │
│  (Docker)                   │
│  - Auth / Quota / History   │
│  - Task Dispatch            │
└─────────────┬──────────────┘
              │ SQL
              ▼
┌────────────────────────────┐
│        PostgreSQL           │
│  (Docker + Volume)          │
└────────────────────────────┘

外部系统：
┌────────────────────────────┐
│         ComfyUI             │
│  GPU Server (Standalone)    │
│  HTTP API                   │
└────────────────────────────┘

3. 核心设计原则（已成立事实）
3.1 事实优先原则（Fact-First）

已上线行为 > 理论最优

已存在数据 > 架构想象

已验证链路 > 潜在设计

3.2 单一事实源（Single Source of Truth）
维度	唯一事实源
用户身份	Backend
权限裁决	Backend
配额扣减	Backend
生成状态	Database
历史记录	Database
4. 前端架构（Frontend）
4.1 技术栈

Vue 3

Vite

Pinia

Axios

Nginx（生产）

4.2 运行形态

仅作为静态资源服务器

不持久化任何业务状态

不做任何权限裁决

4.3 前端职责边界

允许：

页面渲染

用户交互

Token 携带

WebSocket 展示

禁止：

quota 判断

用户身份信任

业务规则计算

5. 后端架构（Backend）
5.1 技术栈

FastAPI

Gunicorn + UvicornWorker

SQLAlchemy

PostgreSQL

5.2 核心职责

用户认证（JWT）

权限裁决（admin / user）

配额扣减与审计

生成任务调度

历史记录管理

5.3 API 设计原则

REST + JSON

明确状态机（pending / success / failed）

所有写操作必须落库

6. 数据库架构（PostgreSQL）
6.1 角色定位

唯一持久化事实存储

不允许前端或算力节点直连

6.2 核心表语义（简述）
表名	语义
users	用户与配额
histories	每一次生成请求
quota_logs	配额变更流水
plans	套餐定义

数据结构自 v1.0.0-beta 起视为不可随意破坏事实

7. 算力系统（ComfyUI）
7.1 架构地位

外部系统

不属于本仓库 Docker 编排

不直接接触用户或数据库

7.2 通信模式

Backend → ComfyUI

HTTP API

异步结果回收（v1.0.2 以后演进）

8. Docker 架构说明
8.1 容器划分原则
容器	是否无状态
frontend	是
backend	是
postgres	否（Volume）
8.2 网络模型

单 bridge 网络

服务名即 DNS

不依赖宿主 IP

9. 安全边界与信任模型
9.1 信任链
Browser ❌
Frontend ❌
Backend ✅
Database ✅

9.2 明确禁止

前端直接访问数据库

前端直连 ComfyUI

使用客户端状态作为业务依据

10. 冻结声明（v1.0.0-beta）

以下事实自 v1.0.0-beta 起冻结：

三容器架构

JWT 认证模型

配额扣减逻辑

History + QuotaLog 双写模型

前端仅展示、后端裁决原则

11. 本文档不包含内容

CDN 架构

分布式调度

多算力负载均衡

CI/CD 流水线

上述内容 属于后续版本演进范畴。

12. 总结

AI Generation Platform 的核心不是“生成图片”，
而是一个 可审计、可演进、可商业化的生成系统。

该架构已被真实用户、真实数据与真实运行环境验证。

Document Status:
✔ Effective
✔ Version-Frozen (v1.0.0-beta)
✔ Production-Grade