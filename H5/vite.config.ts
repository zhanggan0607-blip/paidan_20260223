import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { VantResolver } from '@vant/auto-import-resolver'
import { resolve } from 'path'
import os from 'os'

/**
 * 获取本机局域网IP地址
 */
function getLocalIP(): string {
  const interfaces = os.networkInterfaces()
  for (const name of Object.keys(interfaces)) {
    const nets = interfaces[name]
    if (nets) {
      for (const net of nets) {
        if (net.family === 'IPv4' && !net.internal) {
          return net.address
        }
      }
    }
  }
  return 'localhost'
}

const localIP = getLocalIP()

export default defineConfig(({ mode }) => ({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router'],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [VantResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@sstcp/shared': resolve(__dirname, '../packages/shared/src/index.ts'),
      '@sstcp/shared/utils/status': resolve(__dirname, '../packages/shared/src/utils/status.ts'),
      '@sstcp/shared/utils/format': resolve(__dirname, '../packages/shared/src/utils/format.ts'),
      '@sstcp/shared/api/endpoints': resolve(__dirname, '../packages/shared/src/api/endpoints.ts'),
      '@sstcp/shared/types/api': resolve(__dirname, '../packages/shared/src/types/api.ts'),
      '@sstcp/shared/types/permission': resolve(__dirname, '../packages/shared/src/types/permission.ts')
    }
  },
  base: mode === 'production' ? '/h5/' : '/',
  server: {
    host: true,
    port: 5180,
    strictPort: true,
    hmr: {
      host: localIP,
      port: 5180,
      protocol: 'ws',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        timeout: 30000,
        proxyTimeout: 30000,
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        timeout: 60000,
        proxyTimeout: 60000,
      }
    }
  }
}))
