# ==========================================
# Stage 1: Build frontend (静态资源打包)
# ==========================================
FROM node:20-alpine AS build

# 工程目录
WORKDIR /app

# 仅复制依赖描述文件（最大化 Docker 缓存命中）
COPY package.json package-lock.json ./

# 💡 提速建议：如果你的构建服务器在国内，可以取消下面这行的注释来加速依赖下载
# RUN npm config set registry https://registry.npmmirror.com

# 安装依赖（严格锁版本，适合 CI / 生产环境）
RUN npm ci

# 复制全部前端源码
COPY . .

# 构建生产级静态资源
# ⚠️ 核心架构：此阶段只生成纯静态的 dist，绝对不硬编码任何 API 域名或运行期参数！
RUN npm run build


# ==========================================
# Stage 2: Runtime (运行时动态注入与托管服务)
# ==========================================
FROM nginx:alpine

# 清理 nginx 默认静态目录，防止污染
RUN rm -rf /usr/share/nginx/html/*

# 拷贝前端构建产物（这是完全解耦的通用静态包）
COPY --from=build /app/dist /usr/share/nginx/html

# =========================
# 覆盖 nginx 默认配置 (支持 Vue Router 的 History 模式)
# =========================
COPY nginx.conf /etc/nginx/conf.d/default.conf

# =========================
# ⭐ 核心修缮：拷贝并激活运行时注入脚本
# =========================
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 🛡️ 容错防线：声明默认环境变量
# 防止小白用户在 docker run 时忘记加 -e API_BASE_URL 导致应用彻底崩溃。
# 默认回退到 '/api'，若配合 Nginx Proxy Manager 反代同一域名，依然能完美运行。
ENV API_BASE_URL=/api

EXPOSE 80

# 前端镜像的最终工作流：
# 1. 容器启动瞬间，拦截执行 docker-entrypoint.sh 动态生成 /env.js
# 2. 移交进程控制权，启动 Nginx 托管静态资源
ENTRYPOINT ["/docker-entrypoint.sh"]