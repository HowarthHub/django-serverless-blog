from blog.models.post import Post
from blog.repositories.base_repository import BaseRepository


class PostRepository(BaseRepository[Post]):

    def __init__(self):
        super().__init__(Post)
