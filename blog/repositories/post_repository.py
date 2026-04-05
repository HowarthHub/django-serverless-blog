from blog.models.post import Post
from blog.repositories.base_repository import BaseRepository


class PostRepository(BaseRepository[Post]):

    def __init__(self):
        super().__init__(Post)

    def find_published(self) -> list[Post]:
        return list(self.model.objects.filter(status=Post.Status.PUBLISHED))

    def find_by_slug(self, slug: str) -> Post | None:
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            return None
