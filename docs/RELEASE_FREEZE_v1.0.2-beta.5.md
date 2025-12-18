AI Generation Platform
Release Freeze Declaration — v1.0.2-beta.5
0. 法律地位声明（最高发布约束）

本文档用于正式冻结 AI Generation Platform v1.0.2-beta.5 版本。

自本文档确认之时起：

本项目 v1.0.2-beta.5 版本正式进入冻结态

本冻结声明对：

代码结构

数据模型

API 行为

Docker 交付形态
具有 不可回滚约束力

1. 冻结范围（Scope of Freeze）
1.1 冻结对象

以下内容在 v1.0.2-beta.5 中 视为已确认事实，不得修改：

前端（SPA + Nginx）

后端（FastAPI + Gunicorn）

数据库结构（PostgreSQL）

Docker 化交付形态

用户 / 配额 / 生成 / 历史 全链路

1.2 冻结不包含内容（明确排除）

以下内容 未纳入本次冻结：

CDN 接入策略

对象存储（S3 / OSS）

支付系统

多租户 / 企业账户

风控 / 封号 / 反作弊

2. 架构冻结声明
2.1 系统架构（冻结）
Browser
   ↓
Frontend (Docker + Nginx)
   ↓ /api
Backend (Docker + FastAPI)
   ↓
PostgreSQL (Docker Volume)


前端为 唯一公网入口

后端仅通过 API 提供服务

数据库不暴露公网（推荐）

2.2 容器形态（冻结）
组件	交付方式
frontend	Docker Image
backend	Docker Image
database	官方 postgres 镜像
3. 接口与路由冻结
3.1 API 路由规范（冻结）

所有后端接口统一前缀：/api

WebSocket：/api/ws

前端通过 Nginx 反向代理访问

3.2 行为冻结

quota 在生成提交时扣减

history 在提交时即落库（pending）

用户数据强隔离（user_id）

4. 数据模型冻结
4.1 核心表（冻结）
表名	冻结状态
users	✅
plans	✅
quota_logs	✅
histories	✅
4.2 冻结约束

不允许删除字段

不允许修改字段语义

不允许变更主外键关系

5. 安全模型冻结

JWT 鉴权机制冻结

RBAC（user / admin）冻结

后端裁决权唯一性冻结

前端不具备安全权威冻结

详细内容见：docs/SECURITY.md

6. 运维与交付冻结
6.1 发布方式（冻结）

使用 docker-compose up -d

通过镜像版本控制发布

不允许生产环境手改代码

6.2 环境变量冻结
变量	说明
DATABASE_URL	数据库连接
JWT_SECRET	鉴权密钥
COMFYUI_BASE_URL	推理服务
7. Git 与版本冻结
7.1 Git Tag 约定（冻结）
git tag -a v1.0.2-beta.5 -m "AI Generation Platform v1.0.2-beta.5 (Frozen)"
git push origin v1.0.2-beta.5

7.2 冻结后允许行为

新建 v1.0.1 分支

新建 v1.1.0 规划

编写文档、评估方案

7.3 冻结后禁止行为

❌ 在 main 分支直接改动核心逻辑
❌ 修改数据库结构
❌ 改变接口语义
❌ 在 v1.0.2-beta.5 上继续“试验性开发”

8. 责任与共识声明

本冻结声明确认：

当前版本 可长期稳定运行

适合对外展示 / 内测 / 商业验证

具备继续演进为正式商用版本的基础

9. 最终确认

版本： v1.0.2-beta.5
状态： Frozen
发布日期： 2025-12-17

10. 结语

冻结不是停止，
而是 给系统一个可以被信任的“锚点”。