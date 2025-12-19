# =========================
# Stage 1: Build frontend
# =========================
FROM node:20-alpine AS build

# 工程目录
WORKDIR /app

# 仅复制依赖描述文件（最大化 Docker 缓存命中）
COPY package.json package-lock.json ./

# 安装依赖（严格锁版本，适合 CI / 生产）
RUN npm ci

# 复制全部前端源码
COPY . .

# 构建生产级静态资源
# ⚠️ 此阶段只生成 dist，不绑定任何运行期参数
RUN npm run build


# =========================
# Stage 2: Runtime (Static)
# =========================
FROM nginx:alpine

# 清理 nginx 默认静态目录
RUN rm -rf /usr/share/nginx/html/*

# 拷贝前端构建产物（唯一交付物）
COPY --from=build /app/dist /usr/share/nginx/html

# 拷贝运行期注入脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 前端镜像的唯一职责：
# - 托管静态资源
# - 在启动时注入 API_BASE_URL
ENTRYPOINT ["/docker-entrypoint.sh"]
