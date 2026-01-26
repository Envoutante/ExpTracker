import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        timeout: 600000,  // 10分钟超时，用于长时间的导入操作
        proxyTimeout: 600000  // 代理超时也设置为10分钟
      }
    }
  }
})
