import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from blog.models import Post


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", password="testpass123", email="admin@test.com"
    )


@pytest.fixture
def admin_client(client, admin_user):
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def published_post(db):
    return Post.objects.create(
        title="Published Post",
        slug="published-post",
        content="This is published",
        status=Post.Status.PUBLISHED,
    )


@pytest.fixture
def draft_post(db):
    return Post.objects.create(
        title="Draft Post",
        slug="draft-post",
        content="This is a draft",
        status=Post.Status.DRAFT,
    )


# =============================================================================
# GET /api/posts/ — List posts
# =============================================================================


@pytest.mark.django_db
class TestListPosts:

    def test_returns_200(self, client):
        response = client.get("/api/posts/")
        assert response.status_code == status.HTTP_200_OK

    def test_returns_only_published_posts(self, client, published_post, draft_post):
        response = client.get("/api/posts/")
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Published Post"

    def test_response_structure(self, client, published_post):
        response = client.get("/api/posts/")
        post = response.data[0]
        assert "id" in post
        assert "title" in post
        assert "slug" in post
        assert "content" in post
        assert "status" in post
        assert "created_at" in post
        assert "updated_at" in post

    def test_unauthenticated_access_allowed(self, client):
        response = client.get("/api/posts/")
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# GET /api/posts/:id/ — Retrieve a single post
# =============================================================================


@pytest.mark.django_db
class TestRetrievePost:

    def test_returns_200_for_existing_post(self, client, published_post):
        response = client.get(f"/api/posts/{published_post.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Published Post"

    def test_returns_404_for_nonexistent_post(self, client):
        response = client.get("/api/posts/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_access_allowed(self, client, published_post):
        response = client.get(f"/api/posts/{published_post.id}/")
        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# POST /api/posts/ — Create a post
# =============================================================================


@pytest.mark.django_db
class TestCreatePost:

    def test_admin_can_create_post(self, admin_client):
        payload = {
            "title": "New Post",
            "slug": "new-post",
            "content": "Some content",
            "status": "draft",
        }
        response = admin_client.post("/api/posts/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Post"
        assert response.data["slug"] == "new-post"

    def test_unauthenticated_user_cannot_create(self, client):
        payload = {
            "title": "Hacker Post",
            "slug": "hacker-post",
            "content": "Should fail",
            "status": "published",
        }
        response = client.post("/api/posts/", payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_admin_user_cannot_create(self, client, db):
        regular_user = User.objects.create_user(username="regular", password="pass123")
        client.force_authenticate(user=regular_user)
        payload = {
            "title": "Regular User Post",
            "slug": "regular-post",
            "content": "Should fail",
            "status": "draft",
        }
        response = client.post("/api/posts/", payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_validation_missing_title(self, admin_client):
        payload = {"slug": "no-title", "content": "Missing title", "status": "draft"}
        response = admin_client.post("/api/posts/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    def test_validation_duplicate_slug(self, admin_client, published_post):
        payload = {
            "title": "Duplicate Slug",
            "slug": "published-post",
            "content": "Same slug",
            "status": "draft",
        }
        response = admin_client.post("/api/posts/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "slug" in response.data

    def test_created_post_exists_in_database(self, admin_client):
        payload = {
            "title": "DB Check",
            "slug": "db-check",
            "content": "Verify persistence",
            "status": "published",
        }
        admin_client.post("/api/posts/", payload, format="json")
        assert Post.objects.filter(slug="db-check").exists()


# =============================================================================
# PUT /api/posts/:id/ — Update a post
# =============================================================================


@pytest.mark.django_db
class TestUpdatePost:

    def test_admin_can_update_post(self, admin_client, published_post):
        payload = {
            "title": "Updated Title",
            "slug": "published-post",
            "content": "Updated content",
            "status": "published",
        }
        response = admin_client.put(
            f"/api/posts/{published_post.id}/", payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

    def test_unauthenticated_user_cannot_update(self, client, published_post):
        payload = {
            "title": "Hacked",
            "slug": "published-post",
            "content": "Hacked",
            "status": "published",
        }
        response = client.put(
            f"/api/posts/{published_post.id}/", payload, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404_for_nonexistent_post(self, admin_client):
        payload = {
            "title": "Ghost",
            "slug": "ghost",
            "content": "Not found",
            "status": "draft",
        }
        response = admin_client.put("/api/posts/9999/", payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_can_update_slug_to_same_value(self, admin_client, published_post):
        payload = {
            "title": "Same Slug",
            "slug": "published-post",
            "content": "Keep same slug",
            "status": "published",
        }
        response = admin_client.put(
            f"/api/posts/{published_post.id}/", payload, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_persists_in_database(self, admin_client, published_post):
        payload = {
            "title": "Persisted Update",
            "slug": "published-post",
            "content": "Check DB",
            "status": "published",
        }
        admin_client.put(
            f"/api/posts/{published_post.id}/", payload, format="json"
        )
        published_post.refresh_from_db()
        assert published_post.title == "Persisted Update"


# =============================================================================
# DELETE /api/posts/:id/ — Delete a post
# =============================================================================


@pytest.mark.django_db
class TestDeletePost:

    def test_admin_can_delete_post(self, admin_client, published_post):
        response = admin_client.delete(f"/api/posts/{published_post.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_deleted_post_removed_from_database(self, admin_client, published_post):
        admin_client.delete(f"/api/posts/{published_post.id}/")
        assert not Post.objects.filter(id=published_post.id).exists()

    def test_unauthenticated_user_cannot_delete(self, client, published_post):
        response = client.delete(f"/api/posts/{published_post.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_404_for_nonexistent_post(self, admin_client):
        response = admin_client.delete("/api/posts/9999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
