import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

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
app.use(router)
app.mount('#app')
