const TOKEN_KEY = 'aiweb_token'

export function setToken(token) {
  if (!token) {
    // ⭐ 关键修复：禁止写入空 token
    localStorage.removeItem(TOKEN_KEY)
    return
  }

  localStorage.setItem(TOKEN_KEY, token)
}

export function getToken() {
  const token = localStorage.getItem(TOKEN_KEY)

  // ⭐ 防御式：空字符串视为无 token
  if (!token) return null

  return token
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}
