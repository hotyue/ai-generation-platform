#!/bin/sh
set -e

# =========================================
# 1. 环境变量清洗与推导
# =========================================
# 优先读取 API_BASE_URL，兼容旧版的 VITE_API_BASE_URL，若都为空则默认回退到 '/api'
REAL_URL="${API_BASE_URL:-$VITE_API_BASE_URL}"

# 剥离末尾可能多余的斜杠 (例如将 http://domain.com/ 变成 http://domain.com)
# 防止前端路由拼接时出现 http://domain.com//api 这种错误路径
CLEAN_URL=$(echo "${REAL_URL:-/api}" | sed 's|/*$||')

# =========================================
# 2. 动态生成前端环境配置文件
# =========================================
# 直接将变量写入 Nginx 静态目录下的 env.js
# 这完美呼应了我们刚刚在 index.html 的 <head> 中引入的 <script src="/env.js"></script>
cat <<EOF > /usr/share/nginx/html/env.js
window.__ENV__ = {
  API_BASE_URL: "${CLEAN_URL}"
};
EOF

# =========================================
# 3. 启动日志打印，方便运维排错
# =========================================
echo "==================================================="
echo "[AI Platform Frontend] Initialization Complete!"
echo "[AI Platform Frontend] Runtime API_BASE_URL : ${CLEAN_URL}"
echo "==================================================="

# =========================================
# 4. 移交主进程控制权给 Nginx
# =========================================
# 使用 exec 确保 Nginx 成为 PID 1 的进程，这样容器才能优雅接收 stop 信号
exec nginx -g 'daemon off;'