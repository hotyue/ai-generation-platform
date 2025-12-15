import { defineStore } from 'pinia'
import { login, getMe } from '../api/auth'
import { setToken, clearToken } from '../utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
  }),

  actions: {
    async login(form) {
      const res = await login(form)
      setToken(res.access_token)
      await this.fetchMe()
    },

    async fetchMe() {
      this.user = await getMe()
    },

    logout() {
      this.user = null
      clearToken()
    },
  },
})
