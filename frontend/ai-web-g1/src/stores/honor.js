import { defineStore } from 'pinia'

export const useHonorStore = defineStore('honor', {
  state: () => ({
    star: 0,
    moon: 0,
    sun: 0,
    diamond: 0,
    crown: 0,
    total_success_tasks: 0,
  }),

  actions: {
    setHonor(payload) {
      this.star = payload.star
      this.moon = payload.moon
      this.sun = payload.sun
      this.diamond = payload.diamond
      this.crown = payload.crown
      this.total_success_tasks = payload.total_success_tasks
    },
  },
})
