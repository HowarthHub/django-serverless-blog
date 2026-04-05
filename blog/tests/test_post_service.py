from blog.interfaces.base_repository_interface import BaseRepositoryInterface
from blog.models.post import Post
from blog.services.post_service import PostService


class MockPostRepository(BaseRepositoryInterface[Post]):

    def __init__(self):
        self._store: dict[int, Post] = {}
        self._next_id = 1

    def find_by_id(self, entity_id: int) -> Post | None:
        return self._store.get(entity_id)

    def get_all(self) -> list[Post]:
        return list(self._store.values())

    def save(self, entity: Post) -> Post:
        if not entity.pk:
            entity.pk = self._next_id
            self._next_id += 1
        self._store[entity.pk] = entity
        return entity

    def delete(self, entity_id: int) -> bool:
        if entity_id in self._store:
            del self._store[entity_id]
            return True
        return False


class TestPostService:

    def setup_method(self):
        self.repo = MockPostRepository()
        self.service = PostService(self.repo)

    def test_create_post(self):
        post = self.service.create_post(
            title="Test Post",
            slug="test-post",
            content="Hello world",
            status="draft",
        )
        assert post.pk is not None
        assert post.title == "Test Post"

    def test_get_all_posts(self):
        self.service.create_post(title="Post 1", slug="post-1", content="A", status="draft")
        self.service.create_post(title="Post 2", slug="post-2", content="B", status="draft")
        posts = self.service.get_all_posts()
        assert len(posts) == 2

    def test_get_post_by_id(self):
        created = self.service.create_post(title="Find Me", slug="find-me", content="C", status="draft")
        found = self.service.get_post_by_id(created.pk)
        assert found is not None
        assert found.title == "Find Me"

    def test_get_post_by_id_not_found(self):
        result = self.service.get_post_by_id(999)
        assert result is None

    def test_update_post(self):
        created = self.service.create_post(title="Old Title", slug="old", content="D", status="draft")
        updated = self.service.update_post(created.pk, title="New Title")
        assert updated is not None
        assert updated.title == "New Title"

    def test_update_post_not_found(self):
        result = self.service.update_post(999, title="Nope")
        assert result is None

    def test_delete_post(self):
        created = self.service.create_post(title="Delete Me", slug="delete-me", content="E", status="draft")
        assert self.service.delete_post(created.pk) is True
        assert self.service.get_post_by_id(created.pk) is None

    def test_delete_post_not_found(self):
        assert self.service.delete_post(999) is False
