import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'custom-logger-middleware',
      configureServer(server) {
        console.log('[vite] 中间件已挂载')

        server.middlewares.use((req, res, next) => {
          const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress
          const time = new Date().toISOString()
          console.log(`[${time}] ${ip} ${req.method} ${req.url}`)
          next()
        })
      }
    }
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
})
