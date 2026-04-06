<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Post } from '../../types/post'
import { fetchPosts } from '../../services/posts'

const posts = ref<Post[]>([])
const loading = ref(true)

onMounted(async () => {
  posts.value = await fetchPosts()
  loading.value = false
})
</script>

<template>
  <div>
    <h1 class="text-4xl font-bold mb-8">Blog</h1>

    <p v-if="loading" class="text-gray-500">Loading...</p>

    <div v-else class="space-y-6">
      <article
        v-for="post in posts"
        :key="post.id"
        class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <router-link :to="{ name: 'post', params: { id: post.id } }">
          <h2 class="text-2xl font-semibold mb-2 text-gray-900 hover:text-blue-600">
            {{ post.title }}
          </h2>
        </router-link>
        <p class="text-sm text-gray-500 mb-3">
          {{ new Date(post.created_at).toLocaleDateString() }}
          <span
            class="ml-2 px-2 py-0.5 rounded text-xs font-medium"
            :class="post.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
          >
            {{ post.status }}
          </span>
        </p>
        <p class="text-gray-600 line-clamp-2">{{ post.content }}</p>
      </article>
    </div>
  </div>
</template>
