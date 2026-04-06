from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from blog.repositories.post_repository import PostRepository
from blog.serializers.post_serializer import PostSerializer
from blog.services.post_service import PostService


class PostViewSet(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PostService(PostRepository())

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request):
        posts = self.service.get_all_posts()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = self.service.create_post(**serializer.validated_data)
        output = PostSerializer(post)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        post = self.service.get_post_by_id(int(pk))
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def update(self, request, pk=None):
        post = self.service.get_post_by_id(int(pk))
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_post(int(pk), **serializer.validated_data)
        output = PostSerializer(updated)
        return Response(output.data)

    def destroy(self, request, pk=None):
        deleted = self.service.delete_post(int(pk))
        if not deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
