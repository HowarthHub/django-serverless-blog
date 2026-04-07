from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# T is a placeholder type — replaced with a real model (e.g. Post) when implemented
T = TypeVar("T")


# ABC = Abstract Base Class — cannot be instantiated directly, must be extended
# Generic[T] = makes this class accept a type parameter e.g. BaseRepositoryInterface[Post]
class BaseRepositoryInterface(ABC, Generic[T]):

    # @abstractmethod forces any child class to implement this method
    @abstractmethod
    def find_by_id(self, entity_id: int) -> T | None:
        pass

    # **filters accepts any keyword arguments e.g. get_all(status="published", slug="my-post")
    @abstractmethod
    def get_all(self, **filters) -> list[T]:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        pass
