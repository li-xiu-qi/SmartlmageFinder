import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

// 兼容 ESM 环境下的 __dirname
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

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
  // '@layouts': path.resolve(__dirname, 'src/layouts'), // 目录当前不存在，如需请恢复
         // 类型统一使用 '@/types'（根别名+目录）方案，不再使用 '@types' 专用别名，避免与 DefinitelyTyped 语义冲突
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
        target: 'http://localhost:10050',
        changeOrigin: true,
        secure: false,
        timeout: 60000, // 60秒超时，适合AI推荐等长时间操作
      },
      // 直接代理 /static 以支持后端返回的 public_url=/static/images/xxx
      '/static': {
        target: 'http://localhost:10050',
        changeOrigin: true,
        secure: false,
        timeout: 30000,
      },
    }
  }
})
