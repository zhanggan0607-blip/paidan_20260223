import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import { Loading, Document, FolderOpened, Folder } from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/variables.css'
import './styles/components.css'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.component('Loading', Loading)
app.component('Document', Document)
app.component('FolderOpened', FolderOpened)
app.component('Folder', Folder)

app.config.errorHandler = (err, instance, info) => {
  const errorObj = err instanceof Error ? err : new Error(String(err))
  console.error('[Global Error Handler]', {
    error: errorObj.message,
    stack: errorObj.stack,
    component: instance?.$options?.name || instance?.$options?.__name || 'Unknown',
    info,
  })
}

app.use(pinia)
app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')
