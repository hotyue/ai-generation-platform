# =========================
# Stage 1: Build frontend
# =========================
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 仅复制依赖文件，利用 Docker 缓存
COPY package.json package-lock.json ./

# 安装依赖（生产级，速度快且稳定）
RUN npm ci

# 复制源码
COPY . .

# 构建生产版本
RUN npm run build


# =========================
# Stage 2: Nginx runtime
# =========================
FROM nginx:1.26-alpine

# 删除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 拷贝自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 拷贝前端构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 前台运行 nginx
CMD ["nginx", "-g", "daemon off;"]
