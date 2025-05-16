import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@layouts': path.resolve(__dirname, 'src/layouts'),
      '@types': path.resolve(__dirname, 'src/types'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@assets': path.resolve(__dirname, 'src/assets'),
    }
  },
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:1000',
        changeOrigin: true,
        secure: false,
      },
      '/data': { // 将 './data' 修改为 '/data'
        target: 'http://localhost:1000', // 目标指向后端服务根地址
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/data/, '/static') // 重写路径，将 /data/images/... 替换为 /static/images/...
      }
    }
  }
})
