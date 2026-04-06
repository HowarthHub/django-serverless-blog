<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Post } from '../../types/post'
import { fetchPost } from '../../services/posts'

const route = useRoute()
const post = ref<Post | null>(null)
const loading = ref(true)

onMounted(async () => {
  const id = Number(route.params.id)
  post.value = await fetchPost(id)
  loading.value = false
})
</script>

<template>
  <div>
    <router-link to="/" class="text-blue-600 hover:underline mb-6 inline-block">
      &larr; Back to all posts
    </router-link>

    <p v-if="loading" class="text-gray-500">Loading...</p>

    <article v-else-if="post">
      <h1 class="text-4xl font-bold mb-3 text-gray-900">{{ post.title }}</h1>
      <p class="text-sm text-gray-500 mb-8">
        {{ new Date(post.created_at).toLocaleDateString() }}
        <span
          class="ml-2 px-2 py-0.5 rounded text-xs font-medium"
          :class="post.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
        >
          {{ post.status }}
        </span>
      </p>
      <div class="prose max-w-none text-gray-700 leading-relaxed whitespace-pre-line">
        {{ post.content }}
      </div>
    </article>
  </div>
</template>
