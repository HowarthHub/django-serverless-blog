from blog.interfaces.base_repository_interface import BaseRepositoryInterface
from blog.models.post import Post


class PostService:

    def __init__(self, repository: BaseRepositoryInterface[Post]):
        self.repository = repository

    def get_all_posts(self, **filters) -> list[Post]:
        return self.repository.get_all(**filters)

    def get_post_by_id(self, post_id: int) -> Post | None:
        return self.repository.find_by_id(post_id)

    def create_post(self, **kwargs) -> Post:
        post = Post(**kwargs)
        return self.repository.save(post)

    def update_post(self, post_id: int, **kwargs) -> Post | None:
        post = self.repository.find_by_id(post_id)
        if post is None:
            return None
        for key, value in kwargs.items():
            setattr(post, key, value)
        return self.repository.save(post)

    def delete_post(self, post_id: int) -> bool:
        return self.repository.delete(post_id)
