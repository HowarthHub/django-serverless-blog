import type { Post } from '../../types/post'

const BASE_URL = '/api'

export async function fetchPosts(): Promise<Post[]> {
  const response = await fetch(`${BASE_URL}/posts/`)
  return response.json()
}

export async function fetchPost(id: number): Promise<Post> {
  const response = await fetch(`${BASE_URL}/posts/${id}/`)
  return response.json()
}
