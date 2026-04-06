from typing import Generic, TypeVar

from django.db import models

from blog.interfaces.base_repository_interface import BaseRepositoryInterface

T = TypeVar("T", bound=models.Model)


class BaseRepository(BaseRepositoryInterface[T], Generic[T]):

    def __init__(self, model: type[T]):
        self.model = model

    def find_by_id(self, entity_id: int) -> T | None:
        try:
            return self.model.objects.get(pk=entity_id)
        except self.model.DoesNotExist:
            return None

    def get_all(self, **filters) -> list[T]:
        queryset = self.model.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return list(queryset)

    def save(self, entity: T) -> T:
        entity.save()
        return entity

    def delete(self, entity_id: int) -> bool:
        try:
            entity = self.model.objects.get(pk=entity_id)
            entity.delete()
            return True
        except self.model.DoesNotExist:
            return False
