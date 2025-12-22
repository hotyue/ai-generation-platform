import { defineStore } from 'pinia'
import { login, getMe } from '../api/auth'
import { setToken, clearToken } from '../utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    accountStatus: null, // normal / restricted / banned
  }),

  actions: {
    async login(form) {
      const res = await login(form)
      setToken(res.access_token)
      await this.fetchMe()
    },

    async fetchMe() {
      const me = await getMe()
      this.user = me
      this.accountStatus = me.account_status
    },

    logout() {
      this.user = null
      this.accountStatus = null
      clearToken()
    },
  },
})
