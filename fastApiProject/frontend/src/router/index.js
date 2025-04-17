// src/router/index.js
import {createRouter, createWebHashHistory} from 'vue-router'
import SystemView from '../views/SystemView.vue'
import HomeView from '../views/HomeView.vue'
import DataView from '../views/DataView.vue'
import ChatView from '../views/ChatView.vue'

const routes = [
  {
    path: '/',

    component: HomeView
  },
  {
    path: '/systemview',

    component: SystemView
  },
  {
    path: '/chatview',

    component: ChatView
  }
  ,
  {
    path: '/dataview',

    component: DataView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
