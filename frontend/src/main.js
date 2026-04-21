import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'

localStorage.clear()

createApp(App).use(router).mount('#app')
