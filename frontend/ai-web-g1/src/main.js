import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

import App from './App.vue'
import './style.css'

// ⭐ v1：User State Event WebSocket
// import { connectWS } from '@/utils/ws'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)

// ⭐ 在 Pinia 就绪后，建立 WS 连接（旁路）
//connectWS()

app.mount('#app')
