import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.config.errorHandler = (err, instance, info) => {
  console.error('[Global Error Handler]', {
    error: err,
    component: instance?.$options?.name || instance?.$options?.__name || 'Unknown',
    info,
  })
}

app.use(pinia)
app.use(router)
app.mount('#app')
