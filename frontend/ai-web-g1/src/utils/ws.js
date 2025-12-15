import { useAuthStore } from '@/stores/auth'

let ws

export function connectWS() {
  if (ws) return
  const authStore = useAuthStore()
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${protocol}://${location.host}/ws`)

  ws.onmessage = (e) => {
    try {
      const evt = JSON.parse(e.data)
      authStore.applyUserEvent(evt)
    } catch {}
  }

  ws.onclose = () => {
    ws = null
    setTimeout(connectWS, 2000) // 简单重连
  }
}
