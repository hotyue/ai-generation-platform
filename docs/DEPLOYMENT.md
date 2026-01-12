# AI Generation Platform
Deployment Whitepaper（生产部署白皮书）
## 1. 文档定位与适用范围

本文档用于描述 AI Generation Platform 在 v1.0.0-beta 阶段的标准化生产部署方式。

### 1.1 适用对象

- 运维工程师

- 技术负责人

- 后续接手部署的开发人员

- 自动化 / CI/CD 接入前的人工部署阶段

### 1.2 不在本文档范围内

- 本地开发环境

- 单文件快速启动

- Demo / 实验性部署

- ComfyUI 算力节点部署细节（独立文档）

## 2. 生产部署总览
### 2.1 标准部署形态（冻结）

三容器部署模型：

| 组件  |  	运行方式  |
| ------ | ------ |
| Frontend	 | Docker + Nginx  |
| Backend	 | Docker + Gunicorn  |
| Database	 | Docker + PostgreSQL  |
| ComfyUI	 | 外部 GPU Server  |
### 2.2 部署目标

- 可重复

- 可回滚

- 可横向演进

- 与宿主机最小耦合

## 3. 部署前置条件
### 3.1 操作系统

- Ubuntu 22.04 LTS（推荐）

- x86_64 架构

### 3.2 必须安装的软件
| 软件  |  	最低要求  |
| ------ | ------ |
| Docker Engine	 | ≥ 24.x |
| Docker Compose Plugin	 | ≥ v2 |
| Git	 | 任意稳定版 |

Node / Python 不需要在宿主机安装

## 4. 代码获取与目录要求
### 4.1 仓库结构要求（关键）
ai-generation-platform/
├── backend/
│   ├── Dockerfile
│   └── app/
├── frontend/
│   └── ai-web-g1/
│       ├── Dockerfile
│       ├── nginx.conf
│       └── .env.production
├── docker-compose.yml
└── docs/

### 4.2 获取代码
```bash
git clone <repository-url>
cd ai-generation-platform
```
## 5. 环境变量与配置说明
### 5.1 后端（docker-compose.yml）

后端通过 environment 注入配置，不依赖 .env 文件。

关键变量：

| 变量名  |  	说明  |
| ------ | ------ |
| DATABASE_URL	 | PostgreSQL 连接串  |
| JWT_SECRET	 | JWT 签名密钥  |
| COMFYUI_BASE_URL	 | 外部 ComfyUI API 地址  |
| ENV	 | 固定为 production  |
### 5.2 前端（.env.production）

文件位置：
```text
frontend/ai-web-g1/.env.production
```

示例内容：
```text
VITE_API_BASE=/api
```

⚠️ 该文件 必须在 Docker build 阶段存在
不会在运行时动态注入

## 6. Docker Compose 编排说明
### 6.1 核心设计原则

- 所有服务通过 服务名通信

- 不依赖宿主 IP

- 数据库使用 Volume 持久化

- 前端通过 Nginx 统一入口

### 6.2 标准启动命令
```bash
docker compose up -d --build
```
### 6.3 服务检查
```bash
docker compose ps
```

应看到：
```text
aiweb-db

aiweb-backend

aiweb-frontend
```
均为 Up

## 7. 网络与端口规划
### 7.1 对外暴露端口
| 服务  |  	端口  |  	说明  |
| ------ | ------ | ------ |
| Frontend	 | 80 / 8080 | 	Web 入口  |
| Backend	 | ❌	 | 不直接暴露  |
| PostgreSQL	 | 可选 | 	仅运维需要  |
### 7.2 内部通信
| 通信方向  |  	地址  |
| ------ | ------ |
| Frontend → Backend	 | http://backend:8000  |
| Backend → DB	 | postgresql://db:5432  |
| Backend → ComfyUI	 | 外部地址  |
## 8. Nginx 生产行为说明（Frontend 容器）
### 8.1 职责

- 静态资源服务

- SPA 路由 fallback

- API 反向代理

- WebSocket 转发

### 8.2 明确不做的事情

- 不鉴权

- 不缓存 API

- 不写业务逻辑

## 9. 首次部署后的验证清单
### 9.1 功能验证

-  前端页面可访问

-  用户注册 / 登录成功

-  配额显示正确

-  生成任务可下发

-  历史记录正确归属

### 9.2 架构验证

-  前端不直连数据库

-  API 统一 /api 前缀

-  WebSocket 正常工作

-  多用户数据不串号

## 10. 停止 / 重启 / 更新
### 10.1 停止服务
```bash
docker compose down
```
### 10.2 更新代码并重建
```bash
git pull
docker compose up -d --build
```
## 11. 回滚策略（事实级）

所有版本通过 Git Tag 管理

数据库结构 不允许随意回滚

回滚仅限：

- 前端镜像

- 后端镜像

## 12. 冻结声明（v1.0.0-beta）

以下部署事实自 v1.0.0-beta 起冻结：

- Docker Compose 为唯一部署入口

- 四容器模型

- 前端 Nginx 反代 API

- 后端 Gunicorn 运行模式

## 13. 总结

本部署方案不是“最简单”，
而是 最稳定、最可控、最可扩展 的起点。

它已经通过真实运行环境验证，
是后续 CI/CD、K8s、灰度发布的坚实基础。

Document Status:
✔ Production Ready
✔ Version-Frozen (v1.0.0-beta)
✔ Long-Term Valid