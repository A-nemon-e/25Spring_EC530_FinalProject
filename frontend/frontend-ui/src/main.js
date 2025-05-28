// import { createApp } from 'vue'
// // import './style.css'
// import App from './App.vue'

// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'

// // createApp(App).mount('#app')

// const app = createApp(App)

// app.use(ElementPlus)
// app.mount('#app')
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'   // ✅ 新增引入
import { createPinia } from 'pinia'

import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'

const app = createApp(App)

app.use(router)                 // ✅ 挂载路由
app.use(ElementPlus)
app.use(createPinia())  // 注册 pinia
// app.use(router)

app.mount('#app')
