import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import AutoImport from 'unplugin-auto-import/vite'
import { VantResolver } from '@vant/auto-import-resolver'
import { resolve } from 'path'

export default defineConfig({
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
      '@sstcp/shared/types/permission': resolve(
        __dirname,
        '../packages/shared/src/types/permission.ts'
      ),
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['src/**/*.{test,spec}.{js,ts}'],
    exclude: ['node_modules', 'dist', 'backend-python'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'dist/', '**/*.d.ts', '**/*.config.*', '**/types/**'],
    },
  },
})
