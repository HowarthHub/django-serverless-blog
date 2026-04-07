import pytest

from blog.models import Post
from blog.repositories.base_repository import BaseRepository


@pytest.mark.django_db
class TestBaseRepository:

    def setup_method(self):
        self.repo = BaseRepository(Post)

    def test_save_and_find_by_id(self):
        post = Post(title="Test", slug="test", content="Content", status="draft")
        saved = self.repo.save(post)
        found = self.repo.find_by_id(saved.pk)
        assert found is not None
        assert found.title == "Test"

    def test_find_by_id_returns_none_when_not_found(self):
        assert self.repo.find_by_id(9999) is None

    def test_get_all_returns_all_records(self):
        Post.objects.create(title="A", slug="a", content="A", status="draft")
        Post.objects.create(title="B", slug="b", content="B", status="published")
        results = self.repo.get_all()
        assert len(results) == 2

    def test_get_all_with_filter(self):
        Post.objects.create(title="Draft", slug="draft", content="D", status="draft")
        Post.objects.create(title="Published", slug="pub", content="P", status="published")
        results = self.repo.get_all(status="published")
        assert len(results) == 1
        assert results[0].title == "Published"

    def test_get_all_with_multiple_filters(self):
        Post.objects.create(title="Match", slug="match", content="C", status="published")
        Post.objects.create(title="No Match", slug="no-match", content="C", status="draft")
        results = self.repo.get_all(status="published", slug="match")
        assert len(results) == 1

    def test_get_all_with_no_matches_returns_empty(self):
        Post.objects.create(title="A", slug="a", content="A", status="draft")
        results = self.repo.get_all(status="published")
        assert len(results) == 0

    def test_delete_removes_record(self):
        post = Post.objects.create(title="Delete Me", slug="del", content="D", status="draft")
        assert self.repo.delete(post.pk) is True
        assert self.repo.find_by_id(post.pk) is None

    def test_delete_returns_false_when_not_found(self):
        assert self.repo.delete(9999) is False
