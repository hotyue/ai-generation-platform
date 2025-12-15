# 使用官方 nginx 镜像作为基础镜像
FROM nginx:alpine

# 删除 nginx 默认配置文件
# 因为我们将使用自定义的配置文件
RUN rm /etc/nginx/conf.d/default.conf

# 拷贝我们自定义的 nginx 配置文件到容器中的 nginx 配置目录
# 该配置文件包含了我们自定义的 nginx 配置
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# 拷贝前端构建产物到 nginx 的网页目录
# `dist/` 是前端构建的产物目录，nginx 会直接提供这些文件
COPY dist/ /usr/share/nginx/html/

# 暴露 80 端口，供外部访问
EXPOSE 80

# 启动 nginx 并保持前台运行
# 该命令是必须的，因为 nginx 默认在启动时会进入后台模式，如果没有这个命令，容器会退出
CMD ["nginx", "-g", "daemon off;"]
