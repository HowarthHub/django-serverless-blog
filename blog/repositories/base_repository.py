from typing import Generic, TypeVar

from django.db import models
from django.db.models import Manager

from blog.interfaces.base_repository_interface import BaseRepositoryInterface

# bound=models.Model means T must be a Django Model (or subclass of one)
T = TypeVar("T", bound=models.Model)


# Concrete implementation of the interface using Django ORM
# BaseRepositoryInterface[T] = passes T to the interface so types flow through
# Generic[T] = makes this class itself generic so PostRepository can do BaseRepository[Post]
class BaseRepository(BaseRepositoryInterface[T], Generic[T]):

    # Accepts the model class (e.g. Post) and stores it for querying
    def __init__(self, model: type[T]):
        self.model = model
        self.objects: Manager[T] = model.objects  # type: ignore[attr-defined]

    def find_by_id(self, entity_id: int) -> T | None:
        try:
            return self.objects.get(pk=entity_id)
        except self.model.DoesNotExist:  # type: ignore[attr-defined]
            return None

    # Dynamically builds queries from keyword arguments
    # e.g. get_all(status="published") -> Post.objects.filter(status="published")
    # Supports Django lookups like title__icontains="django"
    def get_all(self, **filters) -> list[T]:
        queryset = self.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return list(queryset)

    def save(self, entity: T) -> T:
        entity.save()
        return entity

    def delete(self, entity_id: int) -> bool:
        try:
            entity = self.objects.get(pk=entity_id)
            entity.delete()
            return True
        except self.model.DoesNotExist:  # type: ignore[attr-defined]
            return False
