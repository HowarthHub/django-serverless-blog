export interface Post {
  id: number
  title: string
  slug: string
  content: string
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
}
