import { createRouter, createWebHistory } from 'vue-router'
import PostList from '../pages/posts/PostList.vue'
import PostDetail from '../pages/posts/PostDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: PostList },
    { path: '/posts/:id', name: 'post', component: PostDetail },
  ],
})

export default router
