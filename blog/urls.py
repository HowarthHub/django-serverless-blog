from rest_framework.routers import DefaultRouter

from blog.views.post_view import PostViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = router.urls
