import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

import { Dialog, Toast, ImagePreview } from 'vant'

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
app.use(Dialog)
app.use(Toast)
app.use(ImagePreview)
app.use(router)
app.mount('#app')
