import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: process.env.VITE_PORT ? parseInt(process.env.VITE_PORT, 10) : undefined,
    proxy: {
      '/api': process.env.VITE_BACKEND_URL || 'http://localhost:5004',
    },
  },
})
