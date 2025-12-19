#!/bin/sh
set -e

# 强制要求运行期注入 API_BASE_URL
if [ -z "$API_BASE_URL" ]; then
  echo "ERROR: API_BASE_URL is not set"
  exit 1
fi

echo "Injecting API_BASE_URL=$API_BASE_URL"

# 仅对构建产物进行一次性替换
# 不修改 index.html，不引入运行时 JS 逻辑
find /usr/share/nginx/html -type f -name "*.js" \
  -exec sed -i "s#__API_BASE_URL__#${API_BASE_URL}#g" {} \;

# 启动 nginx（前台）
exec nginx -g 'daemon off;'
