import http from '../utils/http'

// 登录
export function login(data) {
  return http.post('/auth/login', data)
}

// 注册（⬅️ 新增，关键）
export function register(data) {
  return http.post('/auth/register', data)
}

// 获取当前用户
export function getMe() {
  return http.get('/auth/me')
}
