// Vue 应用的启动入口
// createApp: 创建 Vue 实例
// App.vue: 根组件，所有页面内容从这里开始
// mount('#app'): 把 Vue 实例挂载到 index.html 的 <div id="app"> 上
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
