# AI Generation Platform
Operations Whitepaper（运维白皮书）
## 1. 文档定位与适用范围

本文档用于描述 AI Generation Platform 在 v1.0.0-beta 阶段的标准化运维方式，覆盖：

- 运行监控

- 日志定位

- 常见故障处理

- 数据安全与回滚边界

### 1.1 适用对象

- 生产环境运维人员

- 技术负责人

- 值班/应急处理人员

- 后续平台接手者

## 2. 运维基本原则（冻结事实）
### 2.1 生产系统原则

- 服务可重启 ≠ 数据可重建

- 容器可销毁 ≠ 数据可丢失

- 异常必须可定位

### 2.2 运维核心目标
| 目标  |  	说明  |
| ------ | ------ |
| 稳定性	 | 用户侧无感知 |
| 可观测	 | 问题可追溯 |
| 可回滚	 | 镜像级回退 |
| 可审计	 | 数据有记录 |
## 3. 服务运行状态检查
### 3.1 查看整体服务状态
```bash
docker compose ps
```

期望结果：
```text
frontend → Up

backend → Up

db → Up
```
### 3.2 单容器健康判断（原则）
| 服务  |  	判断依据  |
| ------ | ------ |
| frontend	 | 页面可访问  |
| backend	API  | 可响应  |
| db	 | 容器运行 + 无 crash  |
| ComfyUI	 | 外部 HTTP 可达  |
## 4. 日志体系（事实级）
### 4.1 日志来源划分
| 组件  |  	日志来源 |
| ------ | ------ |
| Frontend	 | Nginx stdout |
| Backend	 | Gunicorn stdout |
| Database	 | PostgreSQL 容器日志 |
### 4.2 查看日志命令
查看所有服务日志
```bash
docker compose logs -f
```
查看单服务日志
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```
### 4.3 后端常见日志类型
| 日志内容	  |  含义 |
| ------ | ----- |
| 401 / 403	 | 鉴权失败 |
| 400	 | 参数或配额问题 |
| 500	 | 后端异常 |
| Timeout	 | ComfyUI 或网络异常 |
## 5. 常见故障处理指南
### 5.1 前端无法访问

检查步骤：

- frontend 容器是否 Up

- Nginx 是否启动

- 端口映射是否正确

- .env.production 是否正确构建

- docker compose logs frontend

### 5.2 API 请求失败

检查顺序：

- backend 容器是否运行

- 前端是否请求 /api

- Nginx 是否正确反代

- backend 日志是否报错

### 5.3 生成任务失败

排查路径：

- Backend → 是否成功下发任务

- ComfyUI → 是否可访问

- 网络 → tailscale / 内网

- History 表 → 是否记录 pending

### 5.4 配额异常 / 用户串号

原则判断：

- 如果 History.user_id 错误 → 后端问题

- 如果前端显示错 → 前端状态缓存问题

事实冻结：

- 所有最终事实以数据库为准

## 6. 数据库运维策略
### 6.1 数据持久化

- 使用 Docker Volume

- 不允许使用匿名 volume

- 不允许随意删除 volume

### 6.2 数据备份（建议）
```bash
docker exec -t aiweb-db \
pg_dump -U aiweb_user aiweb > backup_$(date +%F).sql
```
### 6.3 数据恢复（谨慎）
```bash
psql -U aiweb_user aiweb < backup.sql
```

⚠️ 恢复前必须确认版本兼容

## 7. 重启与恢复策略
### 7.1 推荐重启顺序
```text
Database → Backend → Frontend
```
### 7.2 实际操作
```bash
docker compose restart db
docker compose restart backend
docker compose restart frontend
```
## 8. 升级与回滚
### 8.1 安全升级流程
```bash
git pull
docker compose up -d --build
```
### 8.2 回滚原则（冻结）
| 项目  |  	是否允许  |
| ------ | ------ |
| 前端镜像	 | ✅ |
| 后端镜像	 | ✅ |
| 数据库结构	 | ❌ |
| 历史数据	 | ❌ |
## 9. 安全运维边界
### 9.1 明确禁止的操作

- 直接修改数据库生产数据

- 在容器内手动改代码

- 跳过 Git 版本控制

## 10. 监控与告警（当前阶段）
### 10.1 已具备能力

- 容器存活监控

- 错误日志可追溯

- 用户侧功能验证

### 10.2 未纳入（后续）

- Prometheus

- Grafana

- APM

- 自动告警

## 11. 冻结声明（v1.0.0-beta）

以下运维事实已冻结：

- Docker Compose 运维入口

- 容器日志为唯一日志源

- 数据库 Volume 持久化

- 不允许在线 schema 破坏

## 12. 总结

运维不是“救火”，
而是 用确定性对抗不确定性。

当前运维模型为后续自动化、K8s、灰度发布提供了稳定基座。

Document Status:
- ✔ Production-Ready
- ✔ Version-Frozen (v1.0.0-beta)
- ✔ Long-Term Valid