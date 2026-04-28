import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import viteCompression from 'vite-plugin-compression';
const __dirname = fileURLToPath(new URL('.', import.meta.url));
export default defineConfig(({ mode }) => ({
    plugins: [
        vue(),
        viteCompression({
            algorithm: 'gzip',
            ext: '.gz',
            threshold: 10240,
            deleteOriginFile: false
        })
    ],
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
            '@sstcp/shared': resolve(__dirname, 'packages/shared/src/index.ts')
        }
    },
    server: {
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false
            }
        }
    },
    build: {
        outDir: 'dist',
        sourcemap: false,
        chunkSizeWarningLimit: 500,
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: mode === 'production',
                drop_debugger: mode === 'production',
                pure_funcs: mode === 'production' ? ['console.log', 'console.info', 'console.debug'] : []
            }
        },
        rollupOptions: {
            output: {
                manualChunks: {
                    'vue-vendor': ['vue', 'vue-router', 'pinia'],
                    'element-plus': ['element-plus', '@element-plus/icons-vue'],
                    'axios': ['axios'],
                },
                chunkFileNames: 'assets/js/[name]-[hash].js',
                entryFileNames: 'assets/js/[name]-[hash].js',
                assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
            }
        }
    }
}));
